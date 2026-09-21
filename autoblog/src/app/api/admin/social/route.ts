import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const blogId = url.searchParams.get('blogId');

    let config;
    if (blogId) {
       config = db.prepare('SELECT id, telegramBotToken, telegramChatId, discordWebhookUrl, whatsappApiUrl, whatsappGroupId FROM AgentConfig WHERE blogId = ?').get(blogId);
    } else {
       config = db.prepare('SELECT id, telegramBotToken, telegramChatId, discordWebhookUrl, whatsappApiUrl, whatsappGroupId FROM AgentConfig LIMIT 1').get();
    }

    if (!config) {
      return NextResponse.json({ error: 'Nenhuma AgentConfig encontrada.' }, { status: 404 });
    }

    return NextResponse.json({ success: true, data: config });
  } catch (error: any) {
    console.error('Social API GET Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

export async function PUT(req: Request) {
  try {
    const body = await req.json();
    const { id, telegramBotToken, telegramChatId, discordWebhookUrl, whatsappApiUrl, whatsappGroupId } = body;

    if (!id) {
       return NextResponse.json({ error: 'ID da AgentConfig é obrigatório.' }, { status: 400 });
    }

    const stmt = db.prepare(`
      UPDATE AgentConfig 
      SET 
        telegramBotToken = ?,
        telegramChatId = ?,
        discordWebhookUrl = ?,
        whatsappApiUrl = ?,
        whatsappGroupId = ?
      WHERE id = ?
    `);

    stmt.run(
      telegramBotToken || null, 
      telegramChatId || null, 
      discordWebhookUrl || null, 
      whatsappApiUrl || null, 
      whatsappGroupId || null, 
      id
    );

    return NextResponse.json({ success: true, message: 'Chaves de Integração Social salvas com sucesso!' });
  } catch (error: any) {
    console.error('Social API PUT Error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
