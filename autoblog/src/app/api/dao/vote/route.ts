import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function POST(request: Request) {
  try {
    const { topicId } = await request.json();

    if (!topicId) {
      return NextResponse.json({ success: false, error: 'Topic ID required' }, { status: 400 });
    }

    await db.prepare(`UPDATE DaoTopic SET votes = votes + 1 WHERE id = ?`).run(topicId);

    // Checar se atingiu 100 votos
    const topic = await db.prepare(`SELECT * FROM DaoTopic WHERE id = ?`).get(topicId) as any;
    
    if (topic && topic.votes >= 100 && topic.status === 'pending') {
       await db.prepare(`UPDATE DaoTopic SET status = 'approved' WHERE id = ?`).run(topicId);
       // Aqui poderia engatilhar a API do SWARM em background
       console.log(`[DAO] 🏆 Tópico "${topic.title}" atingiu 100 votos! Enviando para Redação IA.`);
    }

    return NextResponse.json({ success: true, votes: topic.votes, status: topic.status });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
