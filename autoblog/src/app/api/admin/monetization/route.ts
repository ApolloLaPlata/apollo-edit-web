import { NextResponse } from 'next/server';
import db from '@/lib/db';

function getLastNDays(n: number): string[] {
  const days: string[] = [];
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    days.push(d.toISOString().split('T')[0]);
  }
  return days;
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId') || 'global';
    const last30Days = getLastNDays(30);

    let totalClicks = 0;
    let totalRevenue = 0;
    let clicksChart: any[] = [];
    let topLinks: any[] = [];
    let topPosts: any[] = [];
    let recentClicks: any[] = [];

    const blogFilter = blogId === 'global' ? '' : 'WHERE blogId = ?';
    const blogParam = blogId === 'global' ? [] : [blogId];

    // Totais gerais
    const totals = await db.prepare(`
      SELECT COUNT(*) as clicks, SUM(revenue) as revenue
      FROM AffiliateClick ${blogFilter}
    `).get(...blogParam) as any;
    totalClicks = totals?.clicks || 0;
    totalRevenue = totals?.revenue || 0;

    // Gráfico: cliques por dia (últimos 30 dias)
    const clicksPerDay = await db.prepare(`
      SELECT substr(clickedAt, 1, 10) as date, COUNT(*) as clicks, SUM(revenue) as revenue
      FROM AffiliateClick ${blogFilter}
      ${blogFilter ? 'AND' : 'WHERE'} clickedAt >= date('now', '-30 days')
      GROUP BY date ORDER BY date ASC
    `.replace('AND', blogFilter ? 'AND' : 'WHERE')).all(...blogParam) as any[];

    clicksChart = last30Days.map(day => ({
      date: day,
      clicks: (clicksPerDay.find((c: any) => c.date === day)?.clicks) || 0,
      revenue: (clicksPerDay.find((c: any) => c.date === day)?.revenue) || 0
    }));

    // Top Links mais clicados
    topLinks = await db.prepare(`
      SELECT linkLabel, linkUrl, COUNT(*) as clicks, SUM(revenue) as revenue
      FROM AffiliateClick ${blogFilter}
      GROUP BY linkUrl ORDER BY clicks DESC LIMIT 10
    `).all(...blogParam) as any[];

    // Top Posts que geraram mais cliques
    topPosts = await db.prepare(`
      SELECT ac.postId, p.title, p.slug, COUNT(*) as clicks, SUM(ac.revenue) as revenue
      FROM AffiliateClick ac
      LEFT JOIN Post p ON ac.postId = p.id
      ${blogFilter}
      GROUP BY ac.postId ORDER BY clicks DESC LIMIT 5
    `).all(...blogParam) as any[];

    // Cliques recentes
    recentClicks = await db.prepare(`
      SELECT ac.*, p.title as postTitle
      FROM AffiliateClick ac
      LEFT JOIN Post p ON ac.postId = p.id
      ${blogFilter}
      ORDER BY ac.clickedAt DESC LIMIT 20
    `).all(...blogParam) as any[];

    return NextResponse.json({
      success: true,
      data: {
        totalClicks,
        totalRevenue: Number(totalRevenue.toFixed(2)),
        estimatedMonthly: Number((totalRevenue * (30 / Math.max(1, last30Days.length))).toFixed(2)),
        clicksChart,
        topLinks,
        topPosts,
        recentClicks
      }
    });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
