import { NextResponse } from 'next/server';
import db from '@/lib/db';
import {
  ensureTrendForecastTable,
  executeTrendPrediction,
  executeForecastDispatcher,
  executeFullTrendCycle
} from '@/lib/agents/trend_engine';

export async function GET(request: Request) {
  try {
    ensureTrendForecastTable();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    const sql = blogId && blogId !== 'all'
      ? `SELECT * FROM TrendForecast WHERE blogId = ? ORDER BY scheduledFor ASC LIMIT 50`
      : `SELECT * FROM TrendForecast ORDER BY scheduledFor ASC LIMIT 50`;

    const forecasts = blogId && blogId !== 'all'
      ? await db.prepare(sql).all(blogId)
      : await db.prepare(sql).all();

    const stats = {
      queued: (await db.prepare(`SELECT COUNT(*) as c FROM TrendForecast WHERE status = 'queued'`).get() as any)?.c || 0,
      published: (await db.prepare(`SELECT COUNT(*) as c FROM TrendForecast WHERE status = 'published'`).get() as any)?.c || 0,
      expired: (await db.prepare(`SELECT COUNT(*) as c FROM TrendForecast WHERE status = 'expired'`).get() as any)?.c || 0,
    };

    return NextResponse.json({ success: true, forecasts, stats });
  } catch (error: any) {
    console.error('[API TREND GET] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureTrendForecastTable();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_trend') {
      const res = await executeFullTrendCycle(blogId);
      return NextResponse.json(res);
    }
    if (action === 'force_predict') {
      const res = await executeTrendPrediction(blogId);
      return NextResponse.json(res);
    }
    if (action === 'force_dispatch') {
      const res = await executeForecastDispatcher();
      return NextResponse.json(res);
    }
    if (action === 'clear_expired') {
      await db.prepare(`DELETE FROM TrendForecast WHERE status = 'expired'`).run();
      return NextResponse.json({ success: true, message: 'Previsões expiradas apagadas do Oráculo.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API TREND POST] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
