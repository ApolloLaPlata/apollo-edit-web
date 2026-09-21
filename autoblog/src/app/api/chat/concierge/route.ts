import { NextResponse } from 'next/server';
import { chatWithConcierge, ConciergeRequest } from '@/lib/agents/concierge';

// CORS para permitir que o chatbot seja incorporado ou testado externamente se necessário
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

export async function OPTIONS() {
  return NextResponse.json({}, { headers: corsHeaders });
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { blogId, visitorId, postSlug, message, history } = body as ConciergeRequest;

    if (!blogId || !message) {
      return NextResponse.json({ error: 'Parâmetros obrigatórios: blogId e message' }, { status: 400, headers: corsHeaders });
    }

    const res = await chatWithConcierge({
      blogId,
      visitorId: visitorId || 'guest-' + Math.random().toString(36).substring(2, 9),
      postSlug,
      message,
      history: history || []
    });

    if (!res.success) {
      return NextResponse.json({ error: res.error }, { status: 500, headers: corsHeaders });
    }

    return NextResponse.json({ success: true, ...res.data }, { headers: corsHeaders });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500, headers: corsHeaders });
  }
}
