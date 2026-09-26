import { NextResponse } from 'next/server';
import db from '@/lib/db';

export const dynamic = 'force-dynamic';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const type = url.searchParams.get('type') || 'all';

    // 1. Relatório Editorial (Artigos & SEO)
    const posts = await db
      .prepare(`
      SELECT Post.id, Post.title, Post.slug, Post.author, Post.isPublished, Post.createdAt, Post.language, Blog.name as blogName, Blog.domain as blogDomain
      FROM Post
      JOIN Blog ON Post.blogId = Blog.id
      ORDER BY Post.createdAt DESC
    `)
      .all();

    // 2. Auditoria de Monetização & Afiliados
    let clicks: any[] = [];
    try {
      clicks = await db
        .prepare(`
        SELECT AffiliateClick.id, AffiliateClick.createdAt, AffiliateClick.ip, AffiliateLink.title as linkTitle, AffiliateLink.url, AffiliateLink.category
        FROM AffiliateClick
        JOIN AffiliateLink ON AffiliateClick.linkId = AffiliateLink.id
        ORDER BY AffiliateClick.createdAt DESC
        LIMIT 500
      `)
        .all();
    } catch (e) {
      // Tabela pode não ter cliques ou estrutura específica ainda
      clicks = [];
    }

    const affiliateLinks = await db.prepare('SELECT id, title, url, category, clicks, isActive FROM AffiliateLink ORDER BY clicks DESC').all();

    // 3. Telemetria de Sindicância & Cross-Channel
    const syndicatedPosts = posts.filter(
      (p: any) => p.author === 'Sindicato Neural Apollo' || p.slug.includes('-syndicated-')
    );

    // 4. Resumo Geral da Frota (Briefing Executivo)
    const blogs = await db.prepare('SELECT id, name, domain, theme, primaryColor, createdAt FROM Blog').all();
    const categories = await db.prepare('SELECT id, name, slug FROM Category').all();

    const briefing = {
      timestamp: new Date().toISOString(),
      totalBlogs: blogs.length,
      totalPosts: posts.length,
      publishedPosts: posts.filter((p: any) => p.isPublished === 1 || p.isPublished === 'true').length,
      totalSyndicated: syndicatedPosts.length,
      totalAffiliateLinks: affiliateLinks.length,
      totalAffiliateClicks: affiliateLinks.reduce((acc: number, link: any) => acc + (link.clicks || 0), 0),
      totalCategories: categories.length,
    };

    if (type === 'editorial') {
      return NextResponse.json({ success: true, type: 'editorial', data: posts });
    }

    if (type === 'monetization') {
      return NextResponse.json({ success: true, type: 'monetization', data: { affiliateLinks, clicks } });
    }

    if (type === 'syndication') {
      return NextResponse.json({ success: true, type: 'syndication', data: syndicatedPosts });
    }

    return NextResponse.json({
      success: true,
      briefing,
      posts,
      affiliateLinks,
      syndicatedPosts,
      blogs,
    });
  } catch (error: any) {
    console.error('Erro no GET /api/admin/reports:', error);
    return NextResponse.json({ success: false, error: 'Falha ao processar relatórios executivos.' }, { status: 500 });
  }
}
