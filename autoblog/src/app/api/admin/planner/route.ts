import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    let query = `
      SELECT ContentQueue.*, Blog.name as blogName 
      FROM ContentQueue 
      JOIN Blog ON ContentQueue.blogId = Blog.id
    `;
    const params = [];
    
    if (blogId) {
      query += ` WHERE ContentQueue.blogId = ?`;
      params.push(blogId);
    }
    
    query += ` ORDER BY ContentQueue.createdAt DESC`;

    const tasks = await db.prepare(query).all(...params);
    return NextResponse.json({ success: true, tasks });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { blogId, topic } = await request.json();
    if (!blogId || !topic) throw new Error('Dados incompletos');

    const id = crypto.randomUUID();
    await db.prepare(`INSERT INTO ContentQueue (id, blogId, topic) VALUES (?, ?, ?)`).run(id, blogId, topic);

    return NextResponse.json({ success: true, id });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function DELETE(request: Request) {
  try {
    const { id } = await request.json();
    if (!id) throw new Error('ID ausente');

    await db.prepare(`DELETE FROM ContentQueue WHERE id = ?`).run(id);

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
