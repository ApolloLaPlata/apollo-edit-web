import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { createHash } from 'crypto';

// GET /api/affiliate/click?url=...&blogId=...&postId=...&label=...
// Registra o clique e redireciona para o destino
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const url = searchParams.get('url');
    const blogId = searchParams.get('blogId') || '';
    const postId = searchParams.get('postId') || '';
    const label = searchParams.get('label') || 'link';
    const affiliateLinkId = searchParams.get('lid') || '';

    if (!url) {
      return NextResponse.json({ error: 'URL obrigatória' }, { status: 400 });
    }

    // Hash do IP para privacidade (LGPD)
    const ip = request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown';
    const ipHash = createHash('sha256').update(ip).digest('hex').substring(0, 16);

    // Buscar CPC estimado do link
    let estimatedRevenue = 0.50;
    if (affiliateLinkId) {
      const link = await db.prepare('SELECT estimatedCpc FROM AffiliateLink WHERE id = ?').get(affiliateLinkId) as any;
      if (link?.estimatedCpc) estimatedRevenue = link.estimatedCpc;
      // Incrementar contador
      await db.prepare('UPDATE AffiliateLink SET totalClicks = totalClicks + 1 WHERE id = ?').run(affiliateLinkId);
    }

    // Registrar clique
    const clickId = crypto.randomUUID();
    await db.prepare(`
      INSERT INTO AffiliateClick (id, blogId, postId, affiliateLinkId, linkUrl, linkLabel, ipHash, revenue)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(clickId, blogId, postId, affiliateLinkId, url, label, ipHash, estimatedRevenue);

    // Redirecionar para o destino
    return NextResponse.redirect(url, { status: 302 });

  } catch (error: any) {
    console.error('[AFFILIATE CLICK]', error.message);
    // Mesmo com erro, tenta redirecionar
    const url = new URL(request.url).searchParams.get('url');
    if (url) return NextResponse.redirect(url);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
