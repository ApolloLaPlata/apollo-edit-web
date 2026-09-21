import { NextRequest, NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(req: NextRequest) {
  const url = new URL(req.url);
  const blogId = url.searchParams.get('blogId');
  const lang = url.searchParams.get('lang') || 'pt';
  const offset = parseInt(url.searchParams.get('offset') || '0', 10);
  const limit = parseInt(url.searchParams.get('limit') || '6', 10);

  if (!blogId) {
    return NextResponse.json({ error: 'Missing blogId' }, { status: 400 });
  }

  try {
    const posts = db.prepare(`
      SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
      FROM Post
      LEFT JOIN Blog ON Post.blogId = Blog.id
      WHERE Post.blogId = ? AND Post.language = ?
      ORDER BY Post.createdAt DESC
      LIMIT ? OFFSET ?
    `).all(blogId, lang, limit, offset) as any[];

    // Mapeamento idêntico ao page.tsx
    const mapped = posts.map(p => ({
      id: String(p.id),
      title: p.title,
      slug: p.slug,
      contentMd: p.contentMd || '',
      coverImage: p.coverImage || '',
      author: (p.author || '').replace(/Redação IA/gi, p.blog_name || 'Redação Especial') || p.blog_name || 'Redação',
      createdAt: p.createdAt,
      category: p.category || '',
      blog: { name: p.blog_name, domain: p.blog_domain },
    }));

    return NextResponse.json({ posts: mapped });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
