import { NextResponse } from 'next/server';
import db from '@/lib/db';

// Gera os últimos N dias em formato YYYY-MM-DD
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
    const blogId = searchParams.get('blogId');

    if (!blogId) {
      return NextResponse.json({ success: false, error: 'blogId is required' });
    }

    const last14Days = getLastNDays(14);

    if (blogId === 'global') {
      const totalBlogs = await db.prepare('SELECT COUNT(*) as count FROM Blog').get() as any;
      const totalPosts = await db.prepare('SELECT COUNT(*) as count FROM Post').get() as any;
      const totalViews = await db.prepare('SELECT SUM(views) as count FROM Post').get() as any;
      const totalLeads = await db.prepare('SELECT COUNT(*) as count FROM Subscriber').get() as any;
      const totalOpens = await db.prepare('SELECT SUM(opens) as count FROM Subscriber').get() as any;
      const totalClicks = await db.prepare('SELECT COUNT(*) as count FROM AffiliateClick').get() as any;
      const totalRevenue = await db.prepare('SELECT SUM(revenue) as count FROM AffiliateClick').get() as any;

      // Ranking de Canais
      const channelStats = await db.prepare(`
        SELECT 
          Blog.id,
          Blog.name,
          Blog.domain,
          COUNT(Post.id) as postsCount,
          SUM(Post.views) as totalViews
        FROM Blog
        LEFT JOIN Post ON Blog.id = Post.blogId
        GROUP BY Blog.id
        ORDER BY totalViews DESC
      `).all() as any[];

      for (const channel of channelStats) {
        const leads = await db.prepare('SELECT COUNT(*) as count FROM Subscriber WHERE blogId = ?').get(channel.id) as any;
        channel.leadsCount = leads.count || 0;
        channel.totalViews = channel.totalViews || 0;
      }

      // Gráficos Diários
      const getChartData = async (table: string, dateCol: string) => {
        const query = await db.prepare(`
          SELECT substr(${dateCol}, 1, 10) as date, COUNT(*) as count
          FROM ${table}
          WHERE ${dateCol} >= date('now', '-14 days')
          GROUP BY date
          ORDER BY date ASC
        `).all() as any[];
        return last14Days.map(day => ({
          date: day,
          count: (query.find((p: any) => p.date === day)?.count) || 0
        }));
      };

      return NextResponse.json({
        success: true,
        type: 'global',
        stats: {
          totalBlogs: totalBlogs.count,
          totalPosts: totalPosts.count,
          totalViews: totalViews.count || 0,
          totalLeads: totalLeads.count,
          totalOpens: totalOpens.count || 0,
          totalClicks: totalClicks.count || 0,
          totalRevenue: totalRevenue.count || 0,
          leaderboard: channelStats,
          postsChart: await getChartData('Post', 'createdAt'),
          leadsChart: await getChartData('Subscriber', 'createdAt'),
          clicksChart: await getChartData('AffiliateClick', 'clickedAt'),
        }
      });
    } else {
      const blog = await db.prepare('SELECT * FROM Blog WHERE id = ?').get(blogId) as any;
      if (!blog) return NextResponse.json({ success: false, error: 'Blog not found' });

      const postsCount = await db.prepare('SELECT COUNT(*) as count FROM Post WHERE blogId = ?').get(blogId) as any;
      const viewsCount = await db.prepare('SELECT SUM(views) as count FROM Post WHERE blogId = ?').get(blogId) as any;
      const leadsCount = await db.prepare('SELECT COUNT(*) as count FROM Subscriber WHERE blogId = ?').get(blogId) as any;
      const opensCount = await db.prepare('SELECT SUM(opens) as count FROM Subscriber WHERE blogId = ?').get(blogId) as any;
      const clicksCount = await db.prepare('SELECT COUNT(*) as count FROM AffiliateClick WHERE blogId = ?').get(blogId) as any;
      const revCount = await db.prepare('SELECT SUM(revenue) as count FROM AffiliateClick WHERE blogId = ?').get(blogId) as any;

      const topPosts = await db.prepare(`
        SELECT id, title, slug, views, createdAt, language
        FROM Post
        WHERE blogId = ?
        ORDER BY views DESC
        LIMIT 5
      `).all(blogId) as any[];

      // Top Links Afiliados (Performance)
      const topLinks = await db.prepare(`
        SELECT 
          AffiliateLink.keyword as name, 
          COUNT(AffiliateClick.id) as clicks,
          SUM(AffiliateClick.revenue) as revenue
        FROM AffiliateLink
        LEFT JOIN AffiliateClick ON AffiliateLink.id = AffiliateClick.affiliateLinkId
        WHERE AffiliateLink.blogId = ?
        GROUP BY AffiliateLink.id
        ORDER BY clicks DESC
        LIMIT 5
      `).all(blogId) as any[];

      const getChartDataInd = async (table: string, dateCol: string) => {
        const query = await db.prepare(`
          SELECT substr(${dateCol}, 1, 10) as date, COUNT(*) as count
          FROM ${table}
          WHERE blogId = ? AND ${dateCol} >= date('now', '-14 days')
          GROUP BY date
          ORDER BY date ASC
        `).all(blogId) as any[];
        return last14Days.map(day => ({
          date: day,
          count: (query.find((p: any) => p.date === day)?.count) || 0
        }));
      };

      const langDist = await db.prepare(`SELECT language, COUNT(*) as count FROM Post WHERE blogId = ? GROUP BY language`).all(blogId) as any[];

      return NextResponse.json({
        success: true,
        type: 'individual',
        stats: {
          blogName: blog.name,
          posts: postsCount.count,
          views: viewsCount.count || 0,
          leads: leadsCount.count,
          totalOpens: opensCount.count || 0,
          totalClicks: clicksCount.count || 0,
          totalRevenue: revCount.count || 0,
          topPosts,
          topLinks,
          postsChart: await getChartDataInd('Post', 'createdAt'),
          leadsChart: await getChartDataInd('Subscriber', 'createdAt'),
          clicksChart: await getChartDataInd('AffiliateClick', 'clickedAt'),
          langDist
        }
      });
    }

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
