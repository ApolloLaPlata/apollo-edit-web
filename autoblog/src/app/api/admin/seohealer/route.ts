import { NextResponse } from 'next/server';
import db from '@/lib/db';
import {
  ensureSeoHealerTables,
  executeFullSeoHealerCycle,
  executeSeoHealerAudit
} from '@/lib/agents/seo_healer_engine';

export async function GET(request: Request) {
  try {
    ensureSeoHealerTables();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    const sqlLogs = blogId && blogId !== 'all' && blogId !== 'global'
      ? `SELECT * FROM SeoHealerLog WHERE blogId = ? ORDER BY createdAt DESC LIMIT 50`
      : `SELECT * FROM SeoHealerLog ORDER BY createdAt DESC LIMIT 50`;

    const logs = blogId && blogId !== 'all' && blogId !== 'global'
      ? await db.prepare(sqlLogs).all(blogId)
      : await db.prepare(sqlLogs).all();

    // Contagem de matérias que precisam de cura e matérias curadas
    const pendingQuery = blogId && blogId !== 'all' && blogId !== 'global'
      ? await db.prepare(`SELECT COUNT(*) as c FROM Post WHERE blogId = ? AND (metaDescription IS NULL OR schemaOrgJson IS NULL) AND status = 'published'`).get(blogId) as any
      : await db.prepare(`SELECT COUNT(*) as c FROM Post WHERE (metaDescription IS NULL OR schemaOrgJson IS NULL) AND status = 'published'`).get() as any;

    const healedQuery = blogId && blogId !== 'all' && blogId !== 'global'
      ? await db.prepare(`SELECT COUNT(*) as c FROM Post WHERE blogId = ? AND metaDescription IS NOT NULL AND schemaOrgJson IS NOT NULL AND status = 'published'`).get(blogId) as any
      : await db.prepare(`SELECT COUNT(*) as c FROM Post WHERE metaDescription IS NOT NULL AND schemaOrgJson IS NOT NULL AND status = 'published'`).get() as any;

    const stats = {
      pending: pendingQuery?.c || 0,
      healed: healedQuery?.c || 0,
      totalHeals: (await db.prepare(`SELECT COUNT(*) as c FROM SeoHealerLog`).get() as any)?.c || 0,
    };

    return NextResponse.json({ success: true, logs, stats });
  } catch (error: any) {
    console.error('[API SEO HEALER GET] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureSeoHealerTables();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_heal') {
      const res = await executeFullSeoHealerCycle(blogId);
      return NextResponse.json(res);
    }
    if (action === 'clear_logs') {
      await db.prepare(`DELETE FROM SeoHealerLog`).run();
      return NextResponse.json({ success: true, message: 'Logs de Auto-Healing limpos.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API SEO HEALER POST] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
