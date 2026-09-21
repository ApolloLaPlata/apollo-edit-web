import { NextResponse } from 'next/server';
import { addKnowledge } from '@/lib/agents/rag_engine';
import db from '@/lib/db';

export async function POST(request: Request) {
  try {
    const { channelId, sourceName, content } = await request.json();

    if (!channelId || !content) {
      return NextResponse.json({ error: 'channelId e content são obrigatórios' }, { status: 400 });
    }

    // Como os MDs do Codex podem ser grandes, vamos fazer um chunking básico (picotar em parágrafos)
    const chunks = content.split('\n\n').filter((c: string) => c.trim().length > 20);
    
    let successCount = 0;
    
    // Ingerimos cada trecho isoladamente no motor vetorial para a similaridade ser cirúrgica
    for (const chunk of chunks) {
      const added = await addKnowledge(channelId, sourceName || 'Upload_Manual', chunk);
      if (added) successCount++;
    }

    return NextResponse.json({ 
      status: 'success', 
      message: `${successCount} vetores de conhecimento foram integrados ao cérebro do canal ${channelId}.`
    }, { status: 200 });

  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const channelId = searchParams.get('channelId');

    let query = `SELECT id, channelId, sourceName, content, createdAt FROM knowledge_base ORDER BY createdAt DESC LIMIT 50`;
    let rows = [];

    if (channelId) {
      rows = db.prepare(`SELECT id, channelId, sourceName, content, createdAt FROM knowledge_base WHERE channelId = ? ORDER BY createdAt DESC LIMIT 50`).all(channelId);
    } else {
      rows = db.prepare(query).all();
    }

    return NextResponse.json({ status: 'success', data: rows }, { status: 200 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { id } = await request.json();
    if (!id) return NextResponse.json({ error: 'ID ausente' }, { status: 400 });

    db.prepare(`DELETE FROM knowledge_base WHERE id = ?`).run(id);

    return NextResponse.json({ status: 'success', message: 'Memória vetorial apagada com sucesso.' }, { status: 200 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
