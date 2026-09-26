import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';

export async function POST(req: Request) {
  try {
    const { email, blogId } = await req.json();

    if (!email || !blogId) {
      return NextResponse.json({ error: 'Email e Blog são obrigatórios' }, { status: 400 });
    }

    const id = crypto.randomUUID();

    try {
      await db.prepare('INSERT INTO Subscriber (id, email, blogId) VALUES (?, ?, ?)').run(id, email, blogId);
      
      // Fase 88: Compartilhamento Global de Leads (Retargeting)
      try {
        const globalId = crypto.randomUUID();
        await db.prepare('INSERT INTO GlobalLead (id, email, sourceBlogId) VALUES (?, ?, ?)').run(globalId, email, blogId);
      } catch (globalErr: any) {
        // Se já estiver na rede global (UNIQUE email), ignora
      }

      return NextResponse.json({ success: true });
    } catch (dbError: any) {
      if (dbError.message.includes('UNIQUE constraint failed')) {
        return NextResponse.json({ success: true, message: 'Você já está inscrito!' });
      }
      throw dbError;
    }
  } catch (error) {
    return NextResponse.json({ success: false }, { status: 500 });
  }
}
