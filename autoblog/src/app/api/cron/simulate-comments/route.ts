import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';
import { getLightningClient } from '@/lib/llm/lightning-client';

export async function GET(request: Request) {
  try {
    const url = new URL(request.url);
    if (url.searchParams.get('token') !== 'secret-cron') {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Seleciona um Post Alvo aleatório que receberá o comentário (Post A)
    const postA = await db.prepare('SELECT id, blogId, title, contentMd FROM Post WHERE isPublished = 1 ORDER BY RANDOM() LIMIT 1').get() as any;
    
    if (!postA) {
      return NextResponse.json({ error: 'Nenhum post publicado encontrado' }, { status: 400 });
    }

    // Lógica da Federação Fantasma (Cross-Linking SEO): 30% de chance
    let isCrossLinking = Math.random() < 0.30;
    let postB = null;
    let blogB = null;

    if (isCrossLinking) {
      // Busca um Post de outro domínio para fazer Backlink orgânico
      postB = await db.prepare('SELECT id, blogId, title, slug, contentMd FROM Post WHERE isPublished = 1 AND blogId != ? ORDER BY RANDOM() LIMIT 1').get(postA.blogId) as any;
      if (postB) {
        blogB = await db.prepare('SELECT domain FROM Blog WHERE id = ?').get(postB.blogId) as any;
        if (!blogB) {
          isCrossLinking = false;
        } else {
          console.log(`[GHOST FEDERATION 🕸️] Fantasma detectou oportunidade de Backlink cruzado para: ${blogB.domain}/${postB.slug}`);
        }
      } else {
        isCrossLinking = false;
      }
    } else {
      console.log(`[MOTOR FANTASMA 2.0] Lendo o post: "${postA.title}" para gerar UGC padrão...`);
    }

    const client = getLightningClient();
    
    let systemPrompt = `Você é um Simulador de Leitores Reais.
Sua missão é gerar 1 (UM) comentário orgânico, hiper-realista e perfeitamente contextualizado para o texto que o usuário lhe enviar.
O comentário deve soar como um ser humano brasileiro real lendo o artigo na internet.
Regras:
1. Cite algo específico que está no texto ou adicione uma pergunta provocativa.
2. Seja informal, você pode usar uma ou duas gírias leves ou até um errinho sutil de pontuação (ex: "q" no lugar de "que", falta de vírgula).
3. Invente um Nome e Sobrenome comum no Brasil para ser o autor do comentário.
`;

    let userPrompt = `Artigo Atual:\n${postA.title}\n\nTexto Atual:\n${postA.contentMd.substring(0, 1500)}`;

    if (isCrossLinking && postB && blogB) {
      const backlinkUrl = `https://${blogB.domain}/${postB.slug}`;
      systemPrompt += `\n[DIRETRIZ ESPECIAL DE RECOMENDAÇÃO DE LEITURA (BACKLINK)]:
Além de comentar sobre o artigo atual, você DEVE criar uma ponte sutil e natural recomendando que os leitores leiam outro artigo que você viu em outro site.
A URL que você DEVE colar no comentário é exatamente esta: ${backlinkUrl}
Faça isso parecer espontâneo. Exemplo: "Nossa, isso me lembrou muito um outro artigo excelente que vi sobre [Tema B]. Achei o link, é esse aqui: ${backlinkUrl}".`;

      userPrompt += `\n\n[DADOS DO OUTRO ARTIGO PARA RECOMENDAÇÃO]\nTítulo: ${postB.title}\nTrecho: ${postB.contentMd.substring(0, 500)}`;
    }

    systemPrompt += `\n\nRetorne OBRIGATORIAMENTE um JSON EXATO neste formato:
{
  "name": "João Silva",
  "comment": "O comentário super realista e orgânico aqui."
}`;

    const completion = await client.chat.completions.create({
      model: "anthropic/claude-sonnet-4-6",
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      temperature: 0.9
    });

    const responseText = completion.choices[0]?.message?.content || '{}';
    let parsed: any = {};
    try {
      parsed = JSON.parse(responseText);
    } catch(e) {
      const match = responseText.match(/\{[\s\S]*\}/);
      if(match) parsed = JSON.parse(match[0]);
    }

    if (parsed.name && parsed.comment) {
      const encodedName = encodeURIComponent(parsed.name);
      const avatarUrl = `https://ui-avatars.com/api/?name=${encodedName}&background=random&color=fff&size=128`;
      const id = crypto.randomUUID();

      await db.prepare(`
        INSERT INTO Comment (id, postId, authorName, authorAvatar, content, createdAt) 
        VALUES (?, ?, ?, ?, ?, ?)
      `).run(id, postA.id, parsed.name, avatarUrl, parsed.comment, new Date().toISOString());

      const logMsg = isCrossLinking ? `Comentário com Backlink para ${blogB.domain}` : `Comentário gerado`;
      console.log(`[MOTOR FANTASMA 2.0] ${logMsg} injetado com sucesso no post ${postA.id} por ${parsed.name}`);
      return NextResponse.json({ success: true, message: `${logMsg} por ${parsed.name}`, postId: postA.id });
    }

    return NextResponse.json({ error: 'Falha no parse do LLM' }, { status: 500 });

  } catch (error: any) {
    console.error('[MOTOR FANTASMA] Erro:', error.message);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
