import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { ensureGenesisTable, executeFullGenesisCycle, executeCategoryGenesis, executeNicheColonization, executeMonetizationInjection } from '@/lib/agents/genesis_engine';

export async function GET(request: Request) {
  try {
    ensureGenesisTable();
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    let logs = [];
    if (blogId && blogId !== 'all') {
      logs = db.prepare(`SELECT * FROM GenesisLog WHERE blogId = ? ORDER BY createdAt DESC LIMIT 50`).all(blogId);
    } else {
      logs = db.prepare(`SELECT * FROM GenesisLog ORDER BY createdAt DESC LIMIT 50`).all();
    }

    const totalGenesisQuery = db.prepare(`
      SELECT COUNT(*) as c FROM GenesisLog WHERE actionType = 'category_genesis'
    `).get() as any;

    const totalColonizationQuery = db.prepare(`
      SELECT COUNT(*) as c FROM GenesisLog WHERE actionType = 'niche_colonization'
    `).get() as any;

    const totalMonetizationQuery = db.prepare(`
      SELECT COUNT(*) as c FROM GenesisLog WHERE actionType = 'monetization_injection'
    `).get() as any;

    const totalCategoriesQuery = db.prepare(`SELECT COUNT(*) as c FROM Category`).get() as any;

    return NextResponse.json({
      success: true,
      logs,
      stats: {
        totalGenesis: totalGenesisQuery?.c || 0,
        totalColonizations: totalColonizationQuery?.c || 0,
        totalMonetizations: totalMonetizationQuery?.c || 0,
        totalCategories: totalCategoriesQuery?.c || 0
      }
    });
  } catch (error: any) {
    console.error('[API GENESIS GET] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    ensureGenesisTable();
    const body = await request.json();
    const { action, blogId } = body;

    if (action === 'force_full_genesis') {
      console.log(`[API GENESIS] 🌟 Forçando Ciclo Integral de Gênese e Expansão para: ${blogId || 'Todos'}`);
      const res = await executeFullGenesisCycle(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_category_genesis') {
      const res = await executeCategoryGenesis(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_colonization') {
      const res = await executeNicheColonization(blogId);
      return NextResponse.json(res);
    }

    if (action === 'force_monetization') {
      const res = await executeMonetizationInjection(blogId);
      return NextResponse.json(res);
    }

    if (action === 'clear_logs') {
      db.prepare(`DELETE FROM GenesisLog`).run();
      return NextResponse.json({ success: true, message: 'Telemetria de Gênese e Expansão limpa com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação inválida no motor de gênese.' }, { status: 400 });
  } catch (error: any) {
    console.error('[API GENESIS POST] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
