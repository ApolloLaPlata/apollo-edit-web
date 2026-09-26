import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function PUT(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    const body = await req.json();
    
    await db.prepare(`
      UPDATE Post 
      SET title = ?, slug = ?, contentMd = ?, coverImage = ?, author = ?, isPublished = ?, categoryId = ?, updatedAt = CURRENT_TIMESTAMP
      WHERE id = ?
    `).run(
      body.title,
      body.slug,
      body.contentMd,
      body.coverImage,
      body.author,
      body.isPublished ? 1 : 0,
      body.categoryId || null,
      params.id
    );

    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Erro ao atualizar post:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function DELETE(req: Request, props: { params: Promise<{ id: string }> }) {
  try {
    const params = await props.params;
    await db.prepare(`DELETE FROM Post WHERE id = ?`).run(params.id);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error("Erro ao deletar post:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
