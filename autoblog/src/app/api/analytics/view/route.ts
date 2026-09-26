import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function POST(req: Request) {
  try {
    const { postId } = await req.json();

    if (!postId) {
      return NextResponse.json({ error: 'postId obrigatório' }, { status: 400 });
    }

    // Incrementa a contagem de views
    await db.prepare('UPDATE Post SET views = COALESCE(views, 0) + 1 WHERE id = ?').run(postId);

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json({ success: false }, { status: 500 });
  }
}
