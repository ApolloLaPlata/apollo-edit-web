import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const q = searchParams.get('q')?.trim() || '';
    const blogId = searchParams.get('blogId') || '';
    const lang = searchParams.get('lang') || 'pt';

    if (!q || q.length < 2) {
      return NextResponse.json({ success: true, posts: [] });
    }

    const pattern = `%${q}%`;

    let posts: any[];

    if (blogId && blogId !== 'all') {
      posts = await db.prepare(`
        SELECT id, title, slug, coverImage, createdAt, author, language
        FROM Post
        WHERE blogId = ?
          AND language = ?
          AND isPublished = 1
          AND (title LIKE ? OR contentMd LIKE ?)
        ORDER BY createdAt DESC
        LIMIT 15
      `).all(blogId, lang, pattern, pattern);
    } else {
      posts = await db.prepare(`
        SELECT Post.id, Post.title, Post.slug, Post.coverImage, Post.createdAt, Post.author, Post.language,
               Blog.name as blogName, Blog.domain as blogDomain
        FROM Post
        LEFT JOIN Blog ON Post.blogId = Blog.id
        WHERE Post.isPublished = 1
          AND Post.language = ?
          AND (Post.title LIKE ? OR Post.contentMd LIKE ?)
        ORDER BY Post.createdAt DESC
        LIMIT 20
      `).all(lang, pattern, pattern);
    }

    return NextResponse.json({ success: true, posts });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
