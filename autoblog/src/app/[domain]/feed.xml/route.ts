import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request, props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const baseUrl = `https://${decodedDomain}`;

  const blog = await db.prepare('SELECT id, name, description FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog) {
    return new NextResponse('Blog não encontrado', { status: 404 });
  }

  // Busca os últimos 50 posts publicados para gerar o feed RSS
  const posts = await db.prepare(`
    SELECT title, slug, contentMd, createdAt 
    FROM Post 
    WHERE blogId = ? AND isPublished = 1 
    ORDER BY createdAt DESC LIMIT 50
  `).all(blog.id) as any[];

  // Construção do XML do RSS (Padrão RSS 2.0)
  let rssItems = '';
  for (const post of posts) {
    const postUrl = `${baseUrl}/blog/${post.slug}`;
    const pubDate = new Date(post.createdAt).toUTCString();
    
    // Gera uma breve descrição a partir do ContentMD (escapando caracteres especiais para XML)
    let excerpt = post.contentMd.substring(0, 300).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');

    rssItems += `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${postUrl}</link>
      <guid isPermaLink="true">${postUrl}</guid>
      <description>${excerpt}...</description>
      <pubDate>${pubDate}</pubDate>
    </item>`;
  }

  const rssFeed = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>${blog.name || decodedDomain}</title>
    <link>${baseUrl}</link>
    <description>${blog.description || 'Notícias e Análises Automáticas'}</description>
    <language>pt-br</language>
    <atom:link href="${baseUrl}/feed.xml" rel="self" type="application/rss+xml" />
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${rssItems}
  </channel>
</rss>`;

  return new NextResponse(rssFeed, {
    headers: {
      'Content-Type': 'text/xml',
      'Cache-Control': 's-maxage=1800, stale-while-revalidate',
    },
  });
}
