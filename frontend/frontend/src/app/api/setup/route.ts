import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(req: Request) {
  try {
    db.exec(`
      CREATE TABLE IF NOT EXISTS Ads (
        id TEXT PRIMARY KEY,
        blogId TEXT NOT NULL,
        type TEXT NOT NULL,
        code TEXT NOT NULL,
        isActive INTEGER DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(blogId) REFERENCES Blog(id)
      );

      CREATE TABLE IF NOT EXISTS AffiliateLink (
        id TEXT PRIMARY KEY,
        blogId TEXT,
        keyword TEXT NOT NULL,
        url TEXT NOT NULL,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(blogId) REFERENCES Blog(id)
      );
    `);

    return NextResponse.json({ success: true, message: 'Tabela Ads verificada e criada com sucesso!' });
  } catch (error) {
    console.error('Erro ao criar tabela Ads:', error);
    return NextResponse.json({ error: 'Erro interno' }, { status: 500 });
  }
}
