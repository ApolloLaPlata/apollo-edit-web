import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

// Mapeamento de colunas do Kanban para status do ContentQueue
const statusMap: Record<string, string> = {
  ideias: 'pending',
  rascunho: 'writing',
  revisao: 'review',
  publicado: 'published'
};

const columnMap: Record<string, string> = {
  pending: 'ideias',
  writing: 'rascunho',
  error: 'revisao',
  review: 'revisao',
  published: 'publicado',
  done: 'publicado'
};

export async function GET(request: Request) {
  try {
    const queue = await db.prepare('SELECT * FROM ContentQueue ORDER BY createdAt DESC').all() as any[];
    
    // Converte ContentQueue para o formato do Kanban
    const tasks = queue.map(q => ({
      id: q.id,
      title: q.topic,
      assigne: 'AI Engine',
      columnId: columnMap[q.status] || 'ideias',
      createdAt: q.createdAt
    }));

    return NextResponse.json({ success: true, tasks });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { title, columnId } = body;
    
    if (!title) {
      return NextResponse.json({ success: false, error: 'Título é obrigatório.' }, { status: 400 });
    }

    const id = crypto.randomUUID();
    const createdAt = new Date().toISOString();
    const status = statusMap[columnId || 'ideias'] || 'pending';

    // Pega o primeiro blog disponível
    const blog = await db.prepare('SELECT id FROM Blog LIMIT 1').get() as any;
    const blogId = blog ? blog.id : 'global';

    await db.prepare(`
      INSERT INTO ContentQueue (id, blogId, topic, status, createdAt)
      VALUES (?, ?, ?, ?, ?)
    `).run(id, blogId, title, status, createdAt);

    return NextResponse.json({ success: true, task: { id, title, assigne: 'AI Engine', columnId: columnId || 'ideias', createdAt } });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const { id, columnId } = body;
    
    if (!id || !columnId) {
      return NextResponse.json({ success: false, error: 'ID e Coluna são obrigatórios.' }, { status: 400 });
    }

    const status = statusMap[columnId] || 'pending';

    await db.prepare(`
      UPDATE ContentQueue SET status = ? WHERE id = ?
    `).run(status, id);

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');
    
    if (!id) {
      return NextResponse.json({ success: false, error: 'ID é obrigatório.' }, { status: 400 });
    }

    await db.prepare('DELETE FROM ContentQueue WHERE id = ?').run(id);

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
