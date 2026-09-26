import { NextResponse } from 'next/server';
import db from '@/lib/db';
import {
  ensureCrossChannelTables,
  executeFullCrossChannelCycle,
  executeChannelRadarScan,
  executeChannelIntelligence
} from '@/lib/agents/crosschannel_engine';

const PLATFORMS = ['youtube', 'twitter', 'instagram', 'telegram', 'tiktok', 'facebook', 'linkedin', 'google'];

export async function GET(request: Request) {
  try {
    ensureCrossChannelTables();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    // Métricas agrupadas por plataforma
    const metricsQuery = blogId && blogId !== 'all'
      ? await db.prepare(`SELECT platform, metricType, SUM(value) as total, AVG(delta) as avgDelta, trend FROM ChannelMetric WHERE blogId = ? GROUP BY platform, metricType`).all(blogId)
      : await db.prepare(`SELECT platform, metricType, SUM(value) as total, AVG(delta) as avgDelta, trend FROM ChannelMetric GROUP BY platform, metricType`).all();

    // Insights estratégicos mais recentes
    const insightsQuery = blogId && blogId !== 'all'
      ? await db.prepare(`SELECT * FROM CrossChannelInsight WHERE blogId = ? ORDER BY createdAt DESC LIMIT 5`).all(blogId)
      : await db.prepare(`SELECT * FROM CrossChannelInsight ORDER BY createdAt DESC LIMIT 10`).all();

    // Totais gerais
    const totalImpressions = (await db.prepare(`SELECT SUM(value) as s FROM ChannelMetric WHERE metricType = 'impressions'`).get() as any)?.s || 0;
    const totalClicks = (await db.prepare(`SELECT SUM(value) as s FROM ChannelMetric WHERE metricType = 'clicks'`).get() as any)?.s || 0;
    const totalEngagement = (await db.prepare(`SELECT SUM(value) as s FROM ChannelMetric WHERE metricType = 'engagement'`).get() as any)?.s || 0;

    // Monta objeto de métricas por plataforma
    const platformData: Record<string, any> = {};
    for (const platform of PLATFORMS) {
      const pMetrics = (metricsQuery as any[]).filter(m => m.platform === platform);
      platformData[platform] = {
        impressions: pMetrics.find(m => m.metricType === 'impressions')?.total || 0,
        clicks: pMetrics.find(m => m.metricType === 'clicks')?.total || 0,
        engagement: pMetrics.find(m => m.metricType === 'engagement')?.total || 0,
        delta: pMetrics.find(m => m.metricType === 'impressions')?.avgDelta || 0,
        trend: pMetrics.find(m => m.metricType === 'impressions')?.trend || 'stable',
      };
    }

    return NextResponse.json({
      success: true,
      platformData,
      insights: insightsQuery,
      totals: {
        impressions: Math.round(totalImpressions),
        clicks: Math.round(totalClicks),
        engagement: Math.round(totalEngagement),
        ctr: totalImpressions > 0 ? ((totalClicks / totalImpressions) * 100).toFixed(2) : '0.00'
      }
    });
  } catch (error: any) {
    console.error('[API CROSSCHANNEL GET] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureCrossChannelTables();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_scan') {
      const res = await executeFullCrossChannelCycle(blogId);
      return NextResponse.json(res);
    }
    if (action === 'force_radar') {
      const res = await executeChannelRadarScan(blogId);
      return NextResponse.json(res);
    }
    if (action === 'force_intelligence') {
      const res = await executeChannelIntelligence(blogId);
      return NextResponse.json(res);
    }
    if (action === 'clear_metrics') {
      await db.prepare(`DELETE FROM ChannelMetric`).run();
      await db.prepare(`DELETE FROM CrossChannelInsight`).run();
      return NextResponse.json({ success: true, message: 'Métricas e insights de cross-channel limpos com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API CROSSCHANNEL POST] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
