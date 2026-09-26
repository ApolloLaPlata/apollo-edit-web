import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';
import { getLightningClient } from '@/lib/llm/lightning-client';

const WEBHOOK_SECRET = process.env.WHATSAPP_WEBHOOK_SECRET || 'apollo-master-key';
const WHATSAPP_BRIDGE_URL = 'http://127.0.0.1:5001/api/send';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Autenticação simples baseada no token
    const authHeader = request.headers.get('authorization');
    if (authHeader !== `Bearer ${WEBHOOK_SECRET}`) {
      return NextResponse.json({ success: false, error: 'Não autorizado' }, { status: 401 });
    }

    const { body: messageText, from, sender_name, fromMe } = body;

    if (!messageText) {
      return NextResponse.json({ success: false, error: 'Mensagem vazia' }, { status: 400 });
    }

    if (fromMe) {
      return NextResponse.json({ success: true, ignored: true });
    }

    console.log(`[WHATSAPP NEURAL] Recebido de ${sender_name} (${from}): "${messageText}"`);

    const client = getLightningClient();
    if (!client) {
      throw new Error("Lightning Client (Qwen) não configurado");
    }

    const systemPrompt = `Você é o "Gerente de Bolso" (Maestro), uma inteligência artificial que controla uma rede de blogs autônomos.
O Diretor (usuário) te enviou a seguinte mensagem no WhatsApp: "${messageText}"
Você deve analisar o que ele quer e retornar APENAS um objeto JSON. Não inclua Markdown, blocos de código (\`\`\`) ou texto fora do JSON.

Formato OBRIGATÓRIO do JSON:
{
  "intent": "status" | "write" | "oracle" | "unknown",
  "topic": "Se intent for 'write', extraia o tópico do artigo pedido de forma clara (ex: 'O impacto da inflação no Brasil'). Caso contrário, null",
  "domainHint": "Se o Diretor mencionou algum nicho ou site específico, extraia aqui. Senão, null",
  "reply": "Uma resposta sua para o Diretor, confirmando a ação de forma humana, curta e direta, usando emojis e tom de assistente prestativo."
}

Regras:
- "status": se ele quiser saber como estão as coisas, acessos, fila, etc.
- "write": se ele mandar você escrever uma matéria, pauta, post.
- "oracle": se ele quiser invocar o Oráculo para sugerir novas ideias.
- "unknown": qualquer outra conversa fiada.`;

    const completion = await client.chat.completions.create({
      model: "qwen/qwen-2.5-72b-instruct",
      messages: [{ role: 'system', content: systemPrompt }],
      temperature: 0.1, // baixa temperatura para garantir que ele siga o JSON
      response_format: { type: "json_object" }
    });

    const aiResponseRaw = completion.choices[0].message.content || '{"intent":"unknown","reply":"Não entendi."}';
    let aiResponse;
    try {
      aiResponse = JSON.parse(aiResponseRaw);
    } catch (e) {
      aiResponse = { intent: "unknown", reply: "Meu cérebro neural falhou ao formatar a resposta." };
    }

    let finalReply = aiResponse.reply;

    // =============================================
    // EXECUÇÃO DA INTENÇÃO
    // =============================================
    
    if (aiResponse.intent === 'status') {
      const blogs = db.prepare('SELECT COUNT(*) as c FROM Blog').get() as any;
      const queue = db.prepare('SELECT COUNT(*) as c FROM ContentQueue WHERE status = ?').get('pending') as any;
      const posts = db.prepare('SELECT COUNT(*) as c FROM Post').get() as any;
      
      finalReply += `\n\n📊 *Status da Colmeia*\n🌐 Sites Ativos: ${blogs.c}\n📝 Pautas na Fila: ${queue.c}\n✅ Artigos Publicados: ${posts.c}`;
    } 
    else if (aiResponse.intent === 'write' && aiResponse.topic) {
      // Procura o blog. Se ele passou domainHint, tentamos cruzar.
      let targetBlogId = null;
      let targetBlogName = "Global";
      
      if (aiResponse.domainHint) {
        // Tenta achar um blog que o nome ou nicho contenha a hint (case insensitive simples)
        const possibleBlogs = db.prepare('SELECT id, name, niche FROM Blog').all() as any[];
        const hint = aiResponse.domainHint.toLowerCase();
        const found = possibleBlogs.find(b => b.name.toLowerCase().includes(hint) || b.niche.toLowerCase().includes(hint));
        if (found) {
          targetBlogId = found.id;
          targetBlogName = found.name;
        }
      }
      
      if (!targetBlogId) {
        const fallback = db.prepare('SELECT id, name FROM Blog LIMIT 1').get() as any;
        targetBlogId = fallback ? fallback.id : 'global';
        targetBlogName = fallback ? fallback.name : 'Desconhecido';
      }

      db.prepare(`
        INSERT INTO ContentQueue (id, blogId, topic, status, createdAt)
        VALUES (?, ?, ?, ?, ?)
      `).run(crypto.randomUUID(), targetBlogId, aiResponse.topic, 'pending', new Date().toISOString());

      finalReply += `\n\n📝 Pauta injetada no site: *${targetBlogName}*`;
    }

    // =============================================
    // POSTBACK PARA O WHATSAPP (Via Bridge 5001)
    // =============================================
    try {
      await fetch(WHATSAPP_BRIDGE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: from,
          message: finalReply
        })
      });
      console.log(`[WHATSAPP NEURAL] Resposta enviada de volta para ${from}`);
    } catch (e) {
      console.error(`[WHATSAPP NEURAL] Erro ao contatar a Bridge no POSTBACK: ${e}`);
    }

    return NextResponse.json({ success: true, intent: aiResponse.intent });

  } catch (error: any) {
    console.error('[WHATSAPP WEBHOOK] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
