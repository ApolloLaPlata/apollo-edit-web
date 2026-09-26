import { NextResponse } from 'next/server';
import { getLightningClient } from '@/lib/llm/lightning-client';
import db from '@/lib/db';

export async function POST(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    const blogId = params.id;
    
    // 1. Verificar se o blog existe e está ativo
    const blogMeta = db.prepare('SELECT name, domain FROM Blog WHERE id = ?').get(blogId) as any;
    const agentConfig = db.prepare('SELECT isActive FROM AgentConfig WHERE blogId = ?').get(blogId) as any;

    if (!blogMeta) {
      return NextResponse.json({ success: false, error: 'Blog não encontrado.' }, { status: 404 });
    }
    
    if (!agentConfig || agentConfig.isActive === 0) {
      return NextResponse.json({ success: false, error: 'O Enxame está desativado para este blog.' }, { status: 403 });
    }

    // 2. Pedir para a AI inventar uma pauta super quente e viral (Trend Hunter)
    const client = getLightningClient();
    const systemPrompt = `Você é o Diretor de Jornalismo do blog "${blogMeta.name}". 
Sua única tarefa é inventar UMA (1) pauta/título que seja extremamente viral, atual e focada no nicho do blog, para ser escrita agora.
Responda APENAS com a pauta solicitada (uma frase curta), sem nenhuma explicação adicional.
Exemplo: "O colapso silencioso do dólar e como se proteger".`;

    const completion = await client.chat.completions.create({
      model: "llama-3.3-70b-versatile",
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: `Crie a manchete mais atrativa e urgente possível para hoje.` }
      ],
      temperature: 0.9 // Criatividade alta
    });

    const hotTopic = completion.choices[0].message.content?.replace(/["*]/g, '').trim() || "Tendências do Mercado Financeiro";

    console.log(`[AUTO-GENERATE] Pauta escolhida para ${blogMeta.name}: ${hotTopic}`);

    // 3. Disparo assíncrono do Swarm para não dar timeout
    import('@/lib/agents/swarm').then((swarm) => {
      const prompt = agentConfig.personaPrompt || "Seja jornalístico, direto e use tom formal.";
      swarm.executeSwarmPipeline(hotTopic, blogId, prompt).catch(console.error);
    });

    return NextResponse.json({ 
      success: true, 
      topic: hotTopic,
      message: 'O Auto-Pilot disparou o Enxame Base com a pauta surpresa!' 
    });
  } catch (error: any) {
    console.error("[AUTO-GENERATE] Erro:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
