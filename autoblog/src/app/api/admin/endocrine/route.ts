import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { ensureEndocrineTable, executeFullEndocrineCycle, executeHormonalHomeostasis, executeFactCheckingAudit, executeViralBoostInjection } from '@/lib/agents/endocrine_engine';

export async function GET(request: Request) {
  try {
    ensureEndocrineTable();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    let logs = [];
    if (blogId && blogId !== 'all') {
      logs = db.prepare(`SELECT * FROM EndocrineLog WHERE blogId = ? ORDER BY createdAt DESC LIMIT 50`).all(blogId);
    } else {
      logs = db.prepare(`SELECT * FROM EndocrineLog ORDER BY createdAt DESC LIMIT 50`).all();
    }

    const totalHomeostasisQuery = db.prepare(`
      SELECT COUNT(*) as c FROM EndocrineLog WHERE actionType = 'hormone_homeostasis'
    `).get() as any;

    const totalFactCheckQuery = db.prepare(`
      SELECT COUNT(*) as c FROM EndocrineLog WHERE actionType = 'fact_checking'
    `).get() as any;

    const totalViralQuery = db.prepare(`
      SELECT COUNT(*) as c FROM EndocrineLog WHERE actionType = 'viral_boost'
    `).get() as any;

    const auditedPostsQuery = db.prepare(`
      SELECT COUNT(*) as c FROM Post WHERE contentMd LIKE '%[✔ Auditado por Inteligência Editorial]%'
    `).get() as any;

    return NextResponse.json({
      success: true,
      logs,
      stats: {
        totalHomeostasis: totalHomeostasisQuery?.c || 0,
        totalFactChecks: totalFactCheckQuery?.c || 0,
        totalViralBoosts: totalViralQuery?.c || 0,
        auditedPosts: auditedPostsQuery?.c || 0
      }
    });
  } catch (error: any) {
    console.error('[API ENDOCRINE GET] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureEndocrineTable();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_endocrine') {
      console.log(`[API ENDOCRINE] ⚖️ Forçando Ciclo Endócrino Integral para: ${blogId || 'Todos'}`);
      const res = await executeFullEndocrineCycle(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_homeostasis') {
      const res = await executeHormonalHomeostasis(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_factcheck') {
      const res = await executeFactCheckingAudit(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_viralboost') {
      const res = await executeViralBoostInjection(blogId);
      return NextResponse.json(res);
    }

    if (action === 'clear_logs') {
      db.prepare(`DELETE FROM EndocrineLog`).run();
      return NextResponse.json({ success: true, message: 'Telemetria do Sistema Endócrino limpa com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida no motor endócrino.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API ENDOCRINE POST] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
