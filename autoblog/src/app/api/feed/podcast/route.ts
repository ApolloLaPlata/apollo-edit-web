import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { XMLBuilder } from 'fast-xml-parser';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const host = request.headers.get('host') || 'localhost:3000';
    const protocol = host.includes('localhost') ? 'http' : 'https';
    const baseUrl = `${protocol}://${host}`;

    // Get the primary blog info
    const blog = await db.prepare('SELECT id, name, description, domain, primaryColor, logoUrl FROM Blog LIMIT 1').get() as any;
    if (!blog) {
      return new NextResponse('Blog not found', { status: 404 });
    }

    // Get posts that are audio_track
    const posts = await db.prepare(`
      SELECT p.*, c.name as categoryName
      FROM Post p
      LEFT JOIN Category c ON p.categoryId = c.id
      WHERE p.postType = 'audio_track' AND p.isPublished = 1
      ORDER BY p.createdAt DESC
      LIMIT 50
    `).all() as any[];

    // Parse items to XML
    const items = posts.map(post => {
      let audioUrl = '';
      let durationStr = '00:03:00'; // Default 3 mins fallback
      
      try {
        if (post.mediaPayload) {
          const payload = JSON.parse(post.mediaPayload);
          if (payload.playlist && payload.playlist.length > 0) {
            audioUrl = payload.playlist[0].url;
          }
        }
      } catch (e) {}

      if (!audioUrl) return null;
      if (audioUrl.startsWith('/')) {
        audioUrl = baseUrl + audioUrl;
      }

      const coverUrl = post.coverImage?.startsWith('http') 
        ? post.coverImage 
        : (post.coverImage ? baseUrl + post.coverImage : `${baseUrl}/uploads/default_cover.jpg`);

      return {
        title: post.title,
        link: `${baseUrl}/blog/${post.slug}`,
        description: `<![CDATA[${post.summary || post.contentMd.substring(0, 500)}]]>`,
        pubDate: new Date(post.publishedAt || post.createdAt).toUTCString(),
        guid: {
          "@_isPermaLink": "false",
          "#text": post.id
        },
        "itunes:author": "Apollo AI Network",
        "itunes:summary": post.summary || "Um episódio gerado por Inteligência Artificial.",
        "itunes:image": {
          "@_href": coverUrl
        },
        "itunes:duration": durationStr,
        "itunes:explicit": "no",
        "itunes:episodeType": "full",
        enclosure: {
          "@_url": audioUrl,
          "@_type": "audio/mpeg",
          "@_length": "1024000" // Fictitious length in bytes for dynamic generation
        }
      };
    }).filter(i => i !== null);

    const feedObj = {
      "?xml": { "@_version": "1.0", "@_encoding": "UTF-8" },
      rss: {
        "@_version": "2.0",
        "@_xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "@_xmlns:content": "http://purl.org/rss/1.0/modules/content/",
        "@_xmlns:atom": "http://www.w3.org/2005/Atom",
        channel: {
          "atom:link": {
            "@_href": `${baseUrl}/api/feed/podcast`,
            "@_rel": "self",
            "@_type": "application/rss+xml"
          },
          title: blog.name || 'Apollo AI Podcast',
          link: baseUrl,
          language: 'pt-BR',
          copyright: `© ${new Date().getFullYear()} ${blog.name}`,
          description: blog.description || 'As últimas notícias curadas por Inteligência Artificial.',
          "itunes:author": "Apollo AutoBlog",
          "itunes:type": "episodic",
          "itunes:owner": {
            "itunes:name": "Apollo Team",
            "itunes:email": "podcast@apollo.com"
          },
          "itunes:image": {
            "@_href": blog.logoUrl ? (blog.logoUrl.startsWith('http') ? blog.logoUrl : baseUrl + blog.logoUrl) : `${baseUrl}/uploads/default_logo.jpg`
          },
          "itunes:category": [
            { "@_text": "News" },
            { "@_text": "Technology" }
          ],
          "itunes:explicit": "no",
          item: items
        }
      }
    };

    const builder = new XMLBuilder({
      ignoreAttributes: false,
      format: true,
      cdataPropName: "description",
      suppressEmptyNode: true
    });

    const xmlContent = builder.build(feedObj);

    return new NextResponse(xmlContent, {
      status: 200,
      headers: {
        'Content-Type': 'application/xml; charset=utf-8',
        'Cache-Control': 's-maxage=1800, stale-while-revalidate'
      }
    });

  } catch (err: any) {
    console.error("[PODCAST-RSS] Erro ao gerar feed:", err);
    return new NextResponse('Internal Server Error', { status: 500 });
  }
}
