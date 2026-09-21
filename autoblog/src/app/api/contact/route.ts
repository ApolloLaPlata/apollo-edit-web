import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { randomUUID } from 'crypto';

export async function POST(req: Request) {
  try {
    const { name, email, message, domain } = await req.json();

    if (!name || !email || !message || !domain) {
      return NextResponse.json({ error: 'Todos os campos são obrigatórios' }, { status: 400 });
    }

    // Garante que a tabela existe
    db.exec(`
      CREATE TABLE IF NOT EXISTS ContactMessage (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        domain TEXT NOT NULL,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        read INTEGER DEFAULT 0
      )
    `);

    // Insere a mensagem (Usamos randomUUID nativo do node/crypto)
    const insert = db.prepare('INSERT INTO ContactMessage (id, name, email, message, domain) VALUES (?, ?, ?, ?, ?)');
    insert.run(randomUUID(), name, email, message, domain);

    return NextResponse.json({ success: true, message: 'Mensagem enviada com sucesso!' });
  } catch (error) {
    console.error('Erro ao salvar contato:', error);
    return NextResponse.json({ error: 'Erro interno no servidor' }, { status: 500 });
  }
}
