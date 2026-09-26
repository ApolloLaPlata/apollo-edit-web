import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { getLightningClient } from '@/lib/llm/lightning-client';
import crypto from 'crypto';

const MODEL = "llama-3.3-70b-versatile";

export async function POST(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    const { message } = await req.json();
    const blogId = params.id;

    // Busca o blog atual e sua configuração de agente
    const blogRaw = db.prepare(`
      SELECT 
        Blog.*, 
        AgentConfig.id as agentConfig_id, 
        AgentConfig.personaPrompt as agentConfig_personaPrompt
      FROM Blog
      LEFT JOIN AgentConfig ON AgentConfig.blogId = Blog.id
      WHERE Blog.id = ?
    `).get(blogId);

    const blog = blogRaw ? {
      ...(blogRaw as any),
      agentConfig: (blogRaw as any).agentConfig_id ? {
        id: (blogRaw as any).agentConfig_id,
        personaPrompt: (blogRaw as any).agentConfig_personaPrompt
      } : null
    } : null;

    if (!blog) {
      return NextResponse.json({ success: false, error: 'Blog não encontrado' }, { status: 404 });
    }

    if (!blog.agentConfig) {
      // Cria a configuração padrão se não existir
      db.prepare('INSERT INTO AgentConfig (id, blogId, personaPrompt, imageStylePrompt, isActive, postFrequency) VALUES (?, ?, ?, ?, 1, 3)').run(crypto.randomUUID(), blogId, 'Sou uma IA Editora padrão. Foco em clareza e engajamento.', 'photorealistic, cinematic, highly detailed');
      blog.agentConfig = { personaPrompt: 'Sou uma IA Editora padrão. Foco em clareza e engajamento.' };
    }

    const currentPrompt = blog.agentConfig.personaPrompt;

    // Criando o "Meta-Prompt" para a IA:
    // A IA recebe o prompt antigo e a ordem do usuário, e deve decidir o que fazer.
    const metaSystemPrompt = `Você é a IA Editora-Chefe do blog "${blog.name}".
O seu Diretor (humano) vai lhe dar uma ordem no chat.

SEU SYSTEM PROMPT ATUAL É:
"""
${currentPrompt}
"""

Você tem DOIS possíveis comportamentos baseados no que o Diretor pedir:

OPÇÃO 1: Alterar a Personalidade/Linha Editorial (Se a ordem for sobre "seja mais agressivo", "foque em X", "mude o tom")
OPÇÃO 2: Escrever um novo Artigo/Post (Se a ordem for "crie um post sobre X", "escreva sobre Y", "gere uma pauta")

Sua tarefa é classificar a ordem e retornar OBRIGATORIAMENTE um JSON válido neste formato:
{
  "action": "update_persona" OU "generate_post",
  "topic": "Se a action for generate_post, extraia o tema/tópico exato que ele pediu. Se for update_persona, deixe vazio.",
  "new_system_prompt": "Se a action for update_persona, reescreva o System Prompt incorporando a ordem. Senão, repita o prompt atual.",
  "reply_message": "Sua resposta amigável para o Diretor confirmando o que você vai fazer ou o que foi alterado."
}`;

    const client = getLightningClient();
    const completion = await client.chat.completions.create({
      model: MODEL,
      messages: [
        { role: 'system', content: metaSystemPrompt },
        { role: 'user', content: message }
      ],
      response_format: { type: "json_object" },
      temperature: 0.3
    });

    const responseText = completion.choices[0].message.content;
    
    if (!responseText) {
      throw new Error("Resposta vazia da LLM");
    }

    const parsed = JSON.parse(responseText);
    const newPrompt = parsed.new_system_prompt;
    const replyMessage = parsed.reply_message;
    const action = parsed.action;
    const topic = parsed.topic;

    // Só atualiza a persona no banco de dados se a action for update_persona
    if (action === 'update_persona' && newPrompt) {
      db.prepare('UPDATE AgentConfig SET personaPrompt = ? WHERE blogId = ?').run(newPrompt, blogId);
    }

    if (action === 'generate_post' && topic) {
      // Import dinâmico para não travar rota serverless caso algo mude
      import('@/lib/agents/swarm').then((swarm) => {
        swarm.executeSwarmPipeline(topic, blogId, newPrompt || currentPrompt).catch(console.error);
      });
    }

    return NextResponse.json({ 
      success: true, 
      reply: replyMessage,
      newPrompt: newPrompt,
      action: action,
      topic: topic
    });

  } catch (error) {
    console.error("Erro no Chat do Agente:", error);
    return NextResponse.json({ success: false, error: "Falha de processamento LLM" }, { status: 500 });
  }
}
