import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { exec } from 'child_process';

// Autenticação Segura via N8N_MASTER_KEY
const N8N_MASTER_KEY = process.env.N8N_MASTER_KEY || 'N8N_APOLLO_ROOT';

export async function POST(req: Request) {
  try {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || authHeader !== `Bearer ${N8N_MASTER_KEY}`) {
      return NextResponse.json({ error: 'Unauthorized Pipeline' }, { status: 401 });
    }

    const body = await req.json();
    const { action, payload } = body;

    console.log(`🤖 [WEBHOOK N8N] Ação Recebida: ${action}`);

    switch (action) {
      case 'TRIGGER_HYPE_SCOUT':
        // Aciona o script standalone do Hype Scout em background
        exec('node src/scripts/hype_scout.js', (error, stdout, stderr) => {
          if (error) console.error(`HypeScout Error: ${error.message}`);
          if (stderr) console.error(`HypeScout Stderr: ${stderr}`);
          console.log(`HypeScout Output: ${stdout}`);
        });
        return NextResponse.json({ success: true, message: 'Hype Scout Acionado' });

      case 'CREATE_POST_DRAFT':
        // Cria um post como Rascunho (Quarentena/Revisão) -> FASE 113
        const { blogId, title, content, author } = payload;
        const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        
        const insertPost = db.prepare(`
          INSERT INTO Post (id, blogId, title, slug, contentMd, contentHtml, isPublished, author, createdAt, updatedAt)
          VALUES (?, ?, ?, ?, ?, ?, 2, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        `);
        // isPublished = 2 -> QUARENTENA / REVISÃO HUMANA
        
        const postId = `n8n_${Date.now()}`;
        insertPost.run(postId, blogId, title, slug, content, content, author || 'Redação Automática');
        
        return NextResponse.json({ success: true, postId, slug, status: 'Em Quarentena' });

      case 'DELETE_POST':
        const { targetSlug } = payload;
        db.prepare('DELETE FROM Post WHERE slug = ?').run(targetSlug);
        return NextResponse.json({ success: true, message: `Post deletado: ${targetSlug}` });

      default:
        return NextResponse.json({ error: 'Ação Desconhecida' }, { status: 400 });
    }

  } catch (error: any) {
    console.error('N8N Webhook Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
