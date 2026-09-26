import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';
import fs from 'fs';
import path from 'path';

export async function POST(req: Request) {
  try {
    const authHeader = req.headers.get('Authorization');
    const MASTER_KEY = process.env.N8N_MASTER_KEY || 'N8N_APOLLO_ROOT';

    if (!authHeader || authHeader !== `Bearer ${MASTER_KEY}`) {
      return NextResponse.json({ error: 'Acesso Negado à Ingestion API' }, { status: 401 });
    }

    const { rawText, sourceUrl } = await req.json();

    if (!rawText) {
      return NextResponse.json({ error: 'Payload vazio' }, { status: 400 });
    }

    // 1. Simulação do Roteamento de Personas (LLM Rewrite)
    const personasPath = path.resolve(process.cwd(), 'src/scripts/personas.json');
    let personas = [];
    try {
      personas = JSON.parse(fs.readFileSync(personasPath, 'utf8'));
    } catch (e) {
      personas = [{ id: 'default', name: 'Jornalista IA', authorName: 'Redação Automática' }];
    }
    const selectedPersona = personas[Math.floor(Math.random() * personas.length)];

    console.log(`🧠 [INGESTION] Processando texto com Persona: ${selectedPersona.name}`);

    // Criação de Titulo e Slug simulando IA
    const excerpt = rawText.substring(0, 50).replace(/[^a-zA-Z0-9 ]/g, '');
    const title = `Urgente: ${excerpt}...`;
    const slug = `ingest-${crypto.randomBytes(4).toString('hex')}-${Date.now()}`;
    
    // Conteúdo formatado
    const rewrittenHtml = `
      <p><em>Reportagem Exclusiva processada por ${selectedPersona.name}</em></p>
      <p>O ecossistema acaba de capturar uma nova informação crucial vinda diretamente da fonte.</p>
      <blockquote>${rawText.substring(0, 300)}...</blockquote>
      <p>Abaixo seguem os desdobramentos dessa notícia, analisados pela nossa inteligência proprietária. O impacto disso nas métricas atuais é formidável.</p>
      <p>Fonte Original: <a href="${sourceUrl || '#'}">${sourceUrl || 'Desconhecida'}</a></p>
    `;

    // 2. Selecionar o Blog destino (default para o primeiro)
    const firstBlog = db.prepare('SELECT id FROM Blog LIMIT 1').get() as { id: string };
    const blogId = firstBlog ? firstBlog.id : 'master';

    // 3. Checagem de Quarentena (YMYL) - FASE 113
    const ymylKeywords = ['cripto', 'bitcoin', 'dinheiro', 'investimento', 'saúde', 'doença', 'morte', 'golpe', 'crime'];
    const isYMYL = ymylKeywords.some(k => rawText.toLowerCase().includes(k) || selectedPersona.id === 'crypto');
    const publishStatus = isYMYL ? 2 : 1; // 2 = Quarentena, 1 = Publicado

    const postId = crypto.randomUUID();

    // 4. Inserção no Banco
    const insertPost = db.prepare(`
      INSERT INTO Post (id, blogId, title, slug, contentMd, contentHtml, isPublished, author, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    `);

    insertPost.run(postId, blogId, title, slug, rewrittenHtml, rewrittenHtml, publishStatus, selectedPersona.authorName);

    // 5. Disparar Webhook para o Maestro (O Apollo Edit Web agora deve gerar o Mídia/Vídeo para este Post)
    console.log(`🚀 [INGESTION] Matéria criada (Status: ${publishStatus}). Notificando Apollo Edit Web para gerar mídias...`);
    // Em produção: fetch('https://apollo.edit.web/api/webhook/generate-media', { method: 'POST', body: JSON.stringify({ postId, slug, rawText }) });

    return NextResponse.json({ 
      success: true, 
      postId, 
      slug, 
      status: publishStatus === 1 ? 'Publicado' : 'Em Revisão',
      persona: selectedPersona.name 
    });

  } catch (error: any) {
    console.error('Ingestion Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
