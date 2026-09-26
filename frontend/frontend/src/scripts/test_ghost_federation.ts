import db from './src/lib/db';
import crypto from 'crypto';
import { getLightningClient } from './src/lib/llm/lightning-client';

async function testGhost() {
  const postA = db.prepare('SELECT id, blogId, title, contentMd FROM Post WHERE isPublished = 1 ORDER BY RANDOM() LIMIT 1').get() as any;
  if (!postA) { console.log('Nenhum post publicado.'); return; }
  
  console.log('[MOTOR FANTASMA] Lendo post:', postA.title);
  
  const client = getLightningClient();
  let systemPrompt = `Você é um Simulador de Leitores Reais.
Sua missão é gerar 1 (UM) comentário orgânico, hiper-realista e perfeitamente contextualizado.
Retorne um JSON exato no formato: { "name": "Nome Falso", "comment": "Conteúdo" }`;
  let userPrompt = `Artigo Atual:\n${postA.title}\n\nTexto Atual:\n${postA.contentMd.substring(0, 500)}`;

  const completion = await client.chat.completions.create({
    model: 'anthropic/claude-sonnet-4-6',
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: 0.9
  });

  const responseText = completion.choices[0]?.message?.content || '{}';
  let parsed: any = {};
  try { parsed = JSON.parse(responseText); } catch(e) {
    const match = responseText.match(/\{[\s\S]*\}/);
    if(match) parsed = JSON.parse(match[0]);
  }

  if (parsed.name && parsed.comment) {
    console.log('--- COMENTÁRIO GERADO COM SUCESSO ---');
    console.log('Leitor:', parsed.name);
    console.log('Opinião:', parsed.comment);
    
    // Testa persistência no DB
    const avatarUrl = `https://ui-avatars.com/api/?name=${encodeURIComponent(parsed.name)}`;
    const id = crypto.randomUUID();
    db.prepare('INSERT INTO Comment (id, postId, authorName, authorAvatar, content, createdAt) VALUES (?, ?, ?, ?, ?, ?)').run(id, postA.id, parsed.name, avatarUrl, parsed.comment, new Date().toISOString());
    console.log('✅ Salvo no banco de dados SQLite e renderizado na UI do Post!');
  } else {
    console.log('Erro de parse.', responseText);
  }
}
testGhost();
