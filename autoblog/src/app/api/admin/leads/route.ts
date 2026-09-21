import { NextResponse } from 'next/server';
import db from '@/lib/db';

try {
  db.prepare(`CREATE TABLE IF NOT EXISTS Lead (id TEXT PRIMARY KEY, blogId TEXT NOT NULL, email TEXT NOT NULL, name TEXT, source TEXT, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)`).run();
  db.prepare(`CREATE TABLE IF NOT EXISTS NewsletterCampaign (id TEXT PRIMARY KEY, blogId TEXT NOT NULL, subject TEXT NOT NULL, contentHtml TEXT NOT NULL, sentCount INTEGER DEFAULT 0, createdAt TEXT DEFAULT CURRENT_TIMESTAMP)`).run();
} catch (e) {}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    if (!blogId) {
      return NextResponse.json({ success: false, error: 'blogId is required' });
    }

    let leads = [];
    let campaigns = [];

    if (blogId === 'global') {
      leads = db.prepare(`
        SELECT Lead.*, Blog.name as blogName 
        FROM Lead 
        LEFT JOIN Blog ON Lead.blogId = Blog.id
        ORDER BY Lead.createdAt DESC
      `).all();

      campaigns = db.prepare(`
        SELECT NewsletterCampaign.*, Blog.name as blogName 
        FROM NewsletterCampaign 
        LEFT JOIN Blog ON NewsletterCampaign.blogId = Blog.id
        ORDER BY NewsletterCampaign.createdAt DESC
      `).all();
    } else {
      leads = db.prepare(`SELECT * FROM Lead WHERE blogId = ? ORDER BY createdAt DESC`).all(blogId);
      campaigns = db.prepare(`SELECT * FROM NewsletterCampaign WHERE blogId = ? ORDER BY createdAt DESC`).all(blogId);
    }

    return NextResponse.json({ 
      success: true, 
      leads,
      campaigns
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
