import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

export async function GET() {
  try {
    const ads = await db.prepare('SELECT * FROM AdBlock ORDER BY createdAt DESC').all();
    return NextResponse.json({ ads: ads.map((ad: any) => ({
      ...ad,
      isActive: Boolean(ad.isActive)
    })) });
  } catch (error: any) {
    if (error.message.includes('no such table')) {
      // Cria a tabela se não existir (Fail-safe para Fase 114)
      await db.prepare(`
        CREATE TABLE IF NOT EXISTS AdBlock (
          id TEXT PRIMARY KEY,
          name TEXT NOT NULL,
          position TEXT NOT NULL,
          scriptCode TEXT NOT NULL,
          isActive INTEGER DEFAULT 1,
          createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `).run();
      return NextResponse.json({ ads: [] });
    }
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { name, position, scriptCode, isActive } = body;
    const id = crypto.randomUUID();

    // Garante que a tabela existe
    await db.prepare(`
      CREATE TABLE IF NOT EXISTS AdBlock (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        position TEXT NOT NULL,
        scriptCode TEXT NOT NULL,
        isActive INTEGER DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();

    await db.prepare(`
      INSERT INTO AdBlock (id, name, position, scriptCode, isActive)
      VALUES (?, ?, ?, ?, ?)
    `).run(id, name, position, scriptCode, isActive ? 1 : 0);

    return NextResponse.json({ success: true, ad: { id, name, position, scriptCode, isActive } });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    const { id, isActive } = body;

    await db.prepare('UPDATE AdBlock SET isActive = ? WHERE id = ?').run(isActive ? 1 : 0, id);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
