import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function POST(req: Request) {
  try {
    const { postId } = await req.json();

    if (!postId) {
      return NextResponse.json({ error: 'Post ID is required' }, { status: 400 });
    }

    db.prepare('UPDATE Post SET isPublished = 1 WHERE id = ?').run(postId);

    return NextResponse.json({ success: true, message: 'Post liberado e publicado com sucesso!' });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
