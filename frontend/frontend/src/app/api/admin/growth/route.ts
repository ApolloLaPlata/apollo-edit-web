import { NextResponse } from 'next/server';
import { generateBaitForTarget, getBaitStats, recordBaitClick, BaitRequest } from '@/lib/agents/bait_generator';

// Configuração CORS para permitir chamadas da nossa Extensão do Chrome/Edge (Isca Mercadológica)
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders });
}

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const blogId = searchParams.get('blogId') || undefined;

    const result = await getBaitStats(blogId);
    if (!result.success) {
      return NextResponse.json({ error: result.error }, { status: 500, headers: corsHeaders });
    }

    return NextResponse.json(result.stats, { headers: corsHeaders });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500, headers: corsHeaders });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { action } = body;

    if (action === 'record_click') {
      const { baitId } = body;
      if (!baitId) return NextResponse.json({ error: 'baitId obrigatório' }, { status: 400, headers: corsHeaders });
      const res = await recordBaitClick(baitId);
      return NextResponse.json(res, { headers: corsHeaders });
    }

    // Default: generate_bait
    const { blogId, platform, targetUrl, targetTitle, targetAuthor } = body as BaitRequest;
    if (!blogId || !platform || !targetTitle) {
      return NextResponse.json({ error: 'Parâmetros obrigatórios: blogId, platform, targetTitle' }, { status: 400, headers: corsHeaders });
    }

    const res = await generateBaitForTarget({
      blogId,
      platform,
      targetUrl: targetUrl || 'https://youtube.com',
      targetTitle,
      targetAuthor
    });

    if (!res.success) {
      return NextResponse.json({ error: res.error }, { status: 500, headers: corsHeaders });
    }

    return NextResponse.json({ success: true, baits: res.baits }, { headers: corsHeaders });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500, headers: corsHeaders });
  }
}
