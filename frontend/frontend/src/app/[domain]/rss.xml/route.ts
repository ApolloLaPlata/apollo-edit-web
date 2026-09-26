import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ domain: string }> }
) {
  const { domain } = await params;
  const decodedDomain = decodeURIComponent(domain);
  
  // Buscar os dados do Blog
  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  
  if (!blogMeta) {
    return new NextResponse('Blog não encontrado', { status: 404 });
  }

  // Buscar últimos 20 posts aprovados
  const posts = db.prepare(`
    SELECT title, slug, contentMd, coverImage, author, createdAt 
    FROM Post 
    WHERE blogId = ? AND isPublished = 1 
    ORDER BY createdAt DESC 
    LIMIT 20
  `).all(blogMeta.id) as any[];

  const baseUrl = `https://${decodedDomain}`;

  // Formato Padrão Otimizado pro Google News
  const rssXml = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0" 
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:dc="http://purl.org/dc/elements/1.1/"
     xmlns:atom="http://www.w3.org/2005/Atom"
     xmlns:media="http://search.yahoo.com/mrss/">
<channel>
    <title><![CDATA[${blogMeta.name} - Notícias]]></title>
    <link>${baseUrl}</link>
    <description><![CDATA[As últimas notícias e atualizações de ${blogMeta.name}]]></description>
    <language>pt-br</language>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    <atom:link href="${baseUrl}/rss.xml" rel="self" type="application/rss+xml" />
    
    ${posts.map(post => `
    <item>
        <title><![CDATA[${post.title}]]></title>
        <link>${baseUrl}/blog/${post.slug}</link>
        <guid isPermaLink="true">${baseUrl}/blog/${post.slug}</guid>
        <pubDate>${new Date(post.createdAt).toUTCString()}</pubDate>
        <dc:creator><![CDATA[${post.author || 'Redação'}]]></dc:creator>
        <description><![CDATA[${post.contentMd.substring(0, 200).replace(/<[^>]*>?/gm, '')}...]]></description>
        ${post.coverImage ? `<media:content url="${post.coverImage}" medium="image"/>` : ''}
    </item>`).join('')}
</channel>
</rss>`;

  return new NextResponse(rssXml, {
    headers: {
      'Content-Type': 'text/xml; charset=utf-8',
      'Cache-Control': 's-maxage=3600, stale-while-revalidate=86400', // Cache agressivo de 1h
    },
  });
}
