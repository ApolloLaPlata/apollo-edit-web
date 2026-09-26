import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(
  request: Request,
  props: { params: Promise<{ domain: string }> }
) {
  const params = await props.params;
  const domain = decodeURIComponent(params.domain);

  let blog = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(domain) as any;
  if (!blog && domain.includes('localhost')) {
    blog = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  if (!blog) return new NextResponse('Blog not found', { status: 404 });

  const robots = `User-agent: *
Allow: /

Sitemap: https://${domain}/sitemap.xml`;

  return new NextResponse(robots, {
    headers: { 'Content-Type': 'text/plain' }
  });
}
