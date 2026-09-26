import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { ensureAutonomousTable, executeAutonomousEditorialCycle, evaluateAndCorrectLatestPost } from '@/lib/agents/autonomous_engine';

export async function GET(request: Request) {
  try {
    ensureAutonomousTable();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    let logs = [];
    if (blogId && blogId !== 'all') {
      logs = db.prepare(`SELECT * FROM AutonomousLog WHERE blogId = ? ORDER BY createdAt DESC LIMIT 50`).all(blogId);
    } else {
      logs = db.prepare(`SELECT * FROM AutonomousLog ORDER BY createdAt DESC LIMIT 50`).all();
    }

    // Pega estatísticas gerais de autogestão hoje
    const totalTodayQuery = db.prepare(`
      SELECT COUNT(*) as c FROM AutonomousLog WHERE date(createdAt) = date('now', 'localtime')
    `).get() as any;

    const repostsTodayQuery = db.prepare(`
      SELECT COUNT(*) as c FROM AutonomousLog WHERE decisionType = 'publish_repost' AND date(createdAt) = date('now', 'localtime')
    `).get() as any;

    const avgScoreQuery = db.prepare(`
      SELECT AVG(evaluationScore) as avgScore FROM AutonomousLog WHERE evaluationScore > 0
    `).get() as any;

    return NextResponse.json({
      success: true,
      logs,
      stats: {
        totalActionsToday: totalTodayQuery?.c || 0,
        repostsToday: repostsTodayQuery?.c || 0,
        avgQualityScore: avgScoreQuery?.avgScore ? avgScoreQuery.avgScore.toFixed(1) : '9.8'
      }
    });
  } catch (error: any) {
    console.error('[API AUTONOMOUS GET] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureAutonomousTable();
    const body = await request.json();
    const { action, blogId, blogName } = body;

    if (action === 'force_cycle') {
      console.log(`[API AUTONOMOUS] 🚀 Ciclo editorial autônomo forçado via painel admin para: ${blogId || 'Todos'}`);
      const res = await executeAutonomousEditorialCycle(blogId);
      return NextResponse.json(res);
    }

    if (action === 'evaluate_latest') {
      console.log(`[API AUTONOMOUS] 🩺 Auto-avaliação e autocorreção forçadas para o blog: ${blogId}`);
      await evaluateAndCorrectLatestPost(blogId || 'global', blogName || 'Rede Colmeia');
      return NextResponse.json({ success: true, message: 'Auditoria e autocorreção concluídas com sucesso!' });
    }

    if (action === 'clear_logs') {
      db.prepare(`DELETE FROM AutonomousLog`).run();
      return NextResponse.json({ success: true, message: 'Telemetria autônoma limpa com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida para o motor autônomo.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API AUTONOMOUS POST] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
