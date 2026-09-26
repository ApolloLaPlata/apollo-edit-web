import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { generateArticle } from '@/lib/llm/lightning-client';
import { generateModalImage } from '@/lib/media/modal-client';
import crypto from 'crypto';

export async function POST(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    const { topic } = await req.json();
    const blogId = params.id;

    const blog = await db.prepare('SELECT *, activeFeatures FROM Blog WHERE id = ?').get(blogId) as any;
    if (!blog) {
      return NextResponse.json({ success: false, error: 'Blog não encontrado' }, { status: 404 });
    }

    console.log(`🚀 [Gerador] Iniciando pauta sobre: ${topic} (Mídias ativas: ${blog.activeFeatures || 'todas'})`);

    // Passo 1: Writer Bot (Lightning AI com suporte multimídia)
    console.log(`✍️ [Writer] Escrevendo artigo via Lightning AI...`);
    const article = await generateArticle(topic, blog.domain, blog.activeFeatures);
    
    // Passo 2: Designer Bot (Modal Cloud)
    console.log(`🎨 [Designer] Gerando capa no Modal: ${article.imagePrompt}`);
    const imageUrl = await generateModalImage(article.imagePrompt);

    // Passo 3: Salvar no Banco
    const slug = article.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
    const postId = crypto.randomUUID();
    const postType = article.postType || 'article';
    const mediaPayload = article.mediaPayload ? JSON.stringify(article.mediaPayload) : null;

    await db.prepare(`
      INSERT INTO Post (id, blogId, title, slug, contentMd, coverImage, author, isPublished, postType, mediaPayload, createdAt)
      VALUES (?, ?, ?, ?, ?, ?, 'Redação IA', 1, ?, ?, ?)
    `).run(postId, blogId, article.title, slug, article.contentMd, imageUrl, postType, mediaPayload, new Date().toISOString());

    console.log(`✅ [CMS] Post "${article.title}" [Tipo: ${postType}] publicado com sucesso!`);

    return NextResponse.json({ 
      success: true, 
      post: { title: article.title, slug, postType } 
    });

  } catch (error: any) {
    console.error("Erro na rota de Geração:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
