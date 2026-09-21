import { NextResponse } from 'next/server';
import { getConciergeStats } from '@/lib/agents/concierge';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const blogId = searchParams.get('blogId') || undefined;

    const res = await getConciergeStats(blogId);
    if (!res.success) {
      return NextResponse.json({ error: res.error }, { status: 500 });
    }

    return NextResponse.json(res.stats);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
