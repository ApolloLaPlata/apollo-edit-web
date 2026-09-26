import { NextResponse } from 'next/server';
import db from '@/lib/db';

export const dynamic = 'force-dynamic';

// GET: Puxa todos os artigos recentes da rede e a lista de portais para sindicância
export async function GET() {
  try {
    const posts = db
      .prepare(`
      SELECT Post.id, Post.title, Post.slug, Post.coverImage, Post.createdAt, Post.isPublished, Post.blogId, Blog.name as blogName, Blog.domain as blogDomain
      FROM Post
      JOIN Blog ON Post.blogId = Blog.id
      ORDER BY Post.createdAt DESC
      LIMIT 50
    `)
      .all();

    const blogs = db.prepare('SELECT id, name, domain FROM Blog ORDER BY name ASC').all();

    const stats = {
      totalPosts: posts.length,
      totalBlogs: blogs.length,
      syndicatedCount: db
        .prepare("SELECT COUNT(*) as count FROM Post WHERE author = 'Sindicato Neural Apollo' OR contentMd LIKE '%sindicado via Rede Apollo%'")
        .get() as { count: number },
    };

    return NextResponse.json({ success: true, posts, blogs, stats });
  } catch (error: any) {
    console.error('Erro no GET /api/admin/syndicate:', error);
    return NextResponse.json({ success: false, error: 'Falha ao buscar dados de sindicância.' }, { status: 500 });
  }
}

// POST: Realiza o Cross-Post / Sindicância Neural de um artigo para outro portal da frota
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { sourcePostId, targetBlogId, customAngle } = body;

    if (!sourcePostId || !targetBlogId) {
      return NextResponse.json(
        { success: false, error: 'ID do artigo de origem e portal de destino são obrigatórios.' },
        { status: 400 }
      );
    }

    const sourcePost = db.prepare('SELECT * FROM Post WHERE id = ?').get(sourcePostId) as any;
    const targetBlog = db.prepare('SELECT * FROM Blog WHERE id = ?').get(targetBlogId) as any;
    const sourceBlog = db.prepare('SELECT * FROM Blog WHERE id = ?').get(sourcePost?.blogId) as any;

    if (!sourcePost || !targetBlog) {
      return NextResponse.json({ success: false, error: 'Artigo ou Portal destino não encontrado no banco SQLite.' }, { status: 404 });
    }

    if (sourcePost.blogId === targetBlogId) {
      return NextResponse.json(
        { success: false, error: 'O portal de destino deve ser diferente do portal de origem.' },
        { status: 400 }
      );
    }

    // Gerar novo slug único e título adaptado
    const timestamp = Date.now().toString().slice(-4);
    const newSlug = `${sourcePost.slug}-syndicated-${timestamp}`;
    const newTitle = customAngle ? `${sourcePost.title} (${customAngle})` : `${sourcePost.title} [Edição ${targetBlog.name}]`;

    // Adaptar conteúdo injetando canonical backlink para SEO
    const canonicalLink = sourceBlog
      ? `https://${sourceBlog.domain}/blog/${sourcePost.slug}`
      : `#`;
    
    const adaptedContent = `${sourcePost.contentMd}\n\n---\n\n> [!NOTE]\n> **Sindicato Neural Apollo**: Este conteúdo foi selecionado e republicado via cross-channel network. [Acesse a reportagem original em ${sourceBlog?.name || 'Portal de Origem'}](${canonicalLink}).`;

    // Inserir no banco
    const info = db
      .prepare(`
      INSERT INTO Post (blogId, language, title, slug, contentMd, coverImage, author, isPublished, createdAt, updatedAt)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
    `)
      .run(
        targetBlogId,
        sourcePost.language || 'pt',
        newTitle,
        newSlug,
        adaptedContent,
        sourcePost.coverImage || '',
        'Sindicato Neural Apollo',
        1
      );

    return NextResponse.json({
      success: true,
      newPostId: info.lastInsertRowid,
      newSlug,
      targetBlogName: targetBlog.name,
      message: `Artigo sindicado com sucesso para o portal ${targetBlog.name}!`,
    });
  } catch (error: any) {
    console.error('Erro no POST /api/admin/syndicate:', error);
    return NextResponse.json({ success: false, error: error.message || 'Erro ao processar sindicância.' }, { status: 500 });
  }
}
