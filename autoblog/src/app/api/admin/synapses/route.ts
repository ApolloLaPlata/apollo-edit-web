import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { ensureSynapseTable, executeFullSynapseCycle, executeSynapseLinkage, executeTitleOptimization, executeAutoMegaPhoneDispatch } from '@/lib/agents/synapse_engine';

export async function GET(request: Request) {
  try {
    ensureSynapseTable();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    let logs = [];
    if (blogId && blogId !== 'all') {
      logs = await db.prepare(`SELECT * FROM SynapseLog WHERE blogId = ? ORDER BY createdAt DESC LIMIT 50`).all(blogId);
    } else {
      logs = await db.prepare(`SELECT * FROM SynapseLog ORDER BY createdAt DESC LIMIT 50`).all();
    }

    const totalLinksQuery = await db.prepare(`
      SELECT COUNT(*) as c FROM SynapseLog WHERE actionType = 'internal_linkage'
    `).get() as any;

    const totalOptQuery = await db.prepare(`
      SELECT COUNT(*) as c FROM SynapseLog WHERE actionType = 'title_optimization'
    `).get() as any;

    const totalMegaQuery = await db.prepare(`
      SELECT COUNT(*) as c FROM SynapseLog WHERE actionType = 'megaphone_dispatch'
    `).get() as any;

    return NextResponse.json({
      success: true,
      logs,
      stats: {
        totalLinksCreated: totalLinksQuery?.c || 0,
        totalTitlesOptimized: totalOptQuery?.c || 0,
        totalSocialDispatches: totalMegaQuery?.c || 0,
      }
    });
  } catch (error: any) {
    console.error('[API SYNAPSES GET] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureSynapseTable();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_cycle') {
      console.log(`[API SYNAPSES] ⚡ Forçando Ciclo Integral do Sistema Nervoso para: ${blogId || 'Todos'}`);
      const res = await executeFullSynapseCycle(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_linkage') {
      const res = await executeSynapseLinkage(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_title_opt') {
      const res = await executeTitleOptimization(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_megaphone') {
      const res = await executeAutoMegaPhoneDispatch(blogId);
      return NextResponse.json(res);
    }

    if (action === 'clear_logs') {
      await db.prepare(`DELETE FROM SynapseLog`).run();
      return NextResponse.json({ success: true, message: 'Telemetria de sinapses limpa com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida no motor de sinapses.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API SYNAPSES POST] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
