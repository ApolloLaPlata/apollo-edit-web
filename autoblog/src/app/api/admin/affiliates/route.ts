import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

export async function GET() {
  try {
    const links = await db.prepare('SELECT * FROM AffiliateLink ORDER BY createdAt DESC').all();
    return NextResponse.json({ links: links.map((link: any) => ({
      ...link,
      isActive: Boolean(link.isActive)
    })) });
  } catch (error: any) {
    if (error.message.includes('no such table')) {
      // Cria a tabela se não existir (Fail-safe Fase 115)
      await db.prepare(`
        CREATE TABLE IF NOT EXISTS AffiliateLink (
          id TEXT PRIMARY KEY,
          keyword TEXT NOT NULL,
          url TEXT NOT NULL,
          isActive INTEGER DEFAULT 1,
          createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `).run();
      return NextResponse.json({ links: [] });
    }
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { keyword, url, isActive } = body;
    const id = crypto.randomUUID();

    // Garante tabela
    await db.prepare(`
      CREATE TABLE IF NOT EXISTS AffiliateLink (
        id TEXT PRIMARY KEY,
        keyword TEXT NOT NULL,
        url TEXT NOT NULL,
        isActive INTEGER DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();

    await db.prepare(`
      INSERT INTO AffiliateLink (id, keyword, url, isActive)
      VALUES (?, ?, ?, ?)
    `).run(id, keyword.toLowerCase(), url, isActive ? 1 : 0);

    return NextResponse.json({ success: true, link: { id, keyword: keyword.toLowerCase(), url, isActive } });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    const { id, isActive } = body;

    await db.prepare('UPDATE AffiliateLink SET isActive = ? WHERE id = ?').run(isActive ? 1 : 0, id);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
