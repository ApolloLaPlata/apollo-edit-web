import { NextResponse } from 'next/server';
import { runOracleAgent } from '@/lib/agents/oracle';

export async function POST(request: Request) {
  try {
    const { blogId } = await request.json();
    if (!blogId) throw new Error('BlogId não informado');

    const inserted = await runOracleAgent(blogId);

    return NextResponse.json({ success: true, count: inserted });

  } catch (error: any) {
    console.error('[ORACLE API] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

