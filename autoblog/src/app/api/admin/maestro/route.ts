import { NextResponse } from 'next/server';
import { getLightningClient } from '@/lib/llm/lightning-client';
import db from '@/lib/db';
import crypto from 'crypto';

export async function POST(req: Request) {
  try {
    const { prompt } = await req.json();

    if (!prompt) {
      return NextResponse.json({ success: false, error: 'Mensagem vazia.' }, { status: 400 });
    }

    const client = getLightningClient();
    
    // Pega contexto do banco (sites existentes, métricas básicas) para o LLM entender do que estamos falando
    const blogsRaw = await db.prepare('SELECT id, name, domain FROM Blog').all() as any[];
    const blogsContext = blogsRaw.map(b => `- ${b.name} (ID: ${b.id}, Domínio: ${b.domain})`).join('\n');

    const systemPrompt = `Você é o "Maestro", o Cérebro Central (IA) que gerencia todo este CMS Autônomo.
O seu criador (Admin) está falando com você no painel de controle.
Você tem a capacidade de agendar matérias e consultar os sites ativos.

Sites ativos atualmente no banco de dados:
${blogsContext || 'Nenhum site cadastrado ainda.'}

Se o usuário pedir para gerar, escrever ou agendar um artigo/pauta para um site específico, você DEVE retornar a sua resposta em formato JSON contendo a propriedade "action": "CREATE_POST", o "blogId" (id do site que corresponde ao pedido) e o "topic" (o tema do artigo pedido).
Se o usuário fizer qualquer outra pergunta, retorne um JSON com "action": "CHAT" e a sua resposta na propriedade "message".

EXEMPLO DE RESPOSTA DE AÇÃO:
{
  "action": "CREATE_POST",
  "blogId": "id-do-site-encontrado",
  "topic": "Nome do artigo pedido",
  "message": "Entendido. A pauta foi enviada para a fila do robô redator."
}

EXEMPLO DE RESPOSTA NORMAL:
{
  "action": "CHAT",
  "message": "Olá! Temos 3 sites ativos hoje. Como posso ajudar?"
}`;

    const completion = await client.chat.completions.create({
      model: "qwen/qwen-2.5-72b-instruct",
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.2
    });

    const responseText = completion.choices[0].message.content || '{}';
    let parsed: any = {};
    try {
      parsed = JSON.parse(responseText);
    } catch (e) {
      return NextResponse.json({ success: true, message: responseText });
    }

    if (parsed.action === 'CREATE_POST' && parsed.blogId && parsed.topic) {
      const queueId = crypto.randomUUID();
      await db.prepare(`INSERT INTO ContentQueue (id, blogId, topic, status) VALUES (?, ?, ?, 'pending')`)
        .run(queueId, parsed.blogId, parsed.topic);
      
      return NextResponse.json({ 
        success: true, 
        message: parsed.message || `Ordem aceita. Pauta "${parsed.topic}" enviada para a linha de produção do site selecionado.` 
      });
    }

    return NextResponse.json({ success: true, message: parsed.message || 'Comando compreendido, mas sem ação executável mapeada.' });

  } catch (error: any) {
    console.error("[MAESTRO CHAT] Erro:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
