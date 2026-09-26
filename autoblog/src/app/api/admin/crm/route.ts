import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const blogId = searchParams.get('blogId');

    let leads = [];
    let stats = {
      total: 0,
      active: 0,
      bounced: 0,
      today: 0
    };

    if (blogId && blogId !== 'global') {
      leads = await db.prepare('SELECT * FROM Subscriber WHERE blogId = ? ORDER BY createdAt DESC LIMIT 100').all(blogId) as any[];
      stats.total = (await db.prepare('SELECT COUNT(*) as c FROM Subscriber WHERE blogId = ?').get(blogId) as any).c;
      stats.today = (await db.prepare("SELECT COUNT(*) as c FROM Subscriber WHERE blogId = ? AND createdAt >= date('now')").get(blogId) as any).c;
    } else {
      leads = await db.prepare('SELECT Subscriber.*, Blog.name as blogName FROM Subscriber LEFT JOIN Blog ON Subscriber.blogId = Blog.id ORDER BY Subscriber.createdAt DESC LIMIT 100').all() as any[];
      stats.total = (await db.prepare('SELECT COUNT(*) as c FROM Subscriber').get() as any).c;
      stats.today = (await db.prepare("SELECT COUNT(*) as c FROM Subscriber WHERE createdAt >= date('now')").get() as any).c;
    }

    // Mock active and bounced based on total just for presentation until real SMTP webhooks are implemented
    stats.active = Math.round(stats.total * 0.95);
    stats.bounced = Math.round(stats.total * 0.05);

    return NextResponse.json({ success: true, leads, stats });
  } catch (error: any) {
    console.error('CRM API GET Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(req: Request) {
   try {
     const body = await req.json();
     const { action, email } = body;

     if (action === 'seed') {
        // Mocking some data for the UI
        const mockBlogId = 'e22e9e62-c0ff-4f46-b631-4c66e94db6e5'; // Will just pick an existing blog ID if possible
        const existingBlog = await db.prepare('SELECT id FROM Blog LIMIT 1').get() as any;
        const targetBlog = existingBlog ? existingBlog.id : mockBlogId;
        
        const stmt = db.prepare('INSERT INTO Subscriber (id, email, blogId) VALUES (?, ?, ?)');
        for(let i = 1; i <= 5; i++) {
           try {
             stmt.run(`mock-lead-${Date.now()}-${i}`, `usuario_teste_${i}@email.com`, targetBlog);
           } catch(e) { } // ignore unique constraints
        }
        return NextResponse.json({ success: true, message: 'Leads de teste inseridos.' });
     }

     if (action === 'delete') {
         await db.prepare('DELETE FROM Subscriber WHERE email = ?').run(email);
         return NextResponse.json({ success: true, message: 'Lead removido com sucesso.' });
     }

     return NextResponse.json({ success: false, error: 'Ação inválida.' }, { status: 400 });
   } catch(e: any) {
     return NextResponse.json({ success: false, error: e.message }, { status: 500 });
   }
}
