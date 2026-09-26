import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId');

    if (!blogId) return NextResponse.json({ success: false, error: 'blogId is required' });

    let config = await db.prepare(`SELECT * FROM AgentConfig WHERE blogId = ?`).get(blogId) as any;
    
    // Se o canal ainda não tem config, a gente cria uma vazia
    if (!config) {
      await db.prepare(`INSERT INTO AgentConfig (id, blogId, isActive) VALUES (?, ?, 0)`).run(crypto.randomUUID(), blogId);
      config = await db.prepare(`SELECT * FROM AgentConfig WHERE blogId = ?`).get(blogId);
    }

    const blogColors = await db.prepare('SELECT primaryColor, secondaryColor, layoutStyle FROM Blog WHERE id = ?').get(blogId) as any;
    if (blogColors) {
      config = { ...config, ...blogColors };
    }

    return NextResponse.json({ success: true, config });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const { 
      blogId, localMemory, youtubeChannelId, instagramHandle, twitterHandle, rssSniperUrl, 
      telegramBotToken, telegramChatId, discordWebhookUrl, whatsappApiUrl, whatsappGroupId, 
      isActive, postIntervalHours, primaryColor, secondaryColor, layoutStyle 
    } = await request.json();

    if (!blogId) return NextResponse.json({ success: false, error: 'blogId is required' });

    const activeInt = isActive ? 1 : 0;

    const stmt = db.prepare(`
      UPDATE AgentConfig 
      SET youtubeChannelId = ?, instagramHandle = ?, twitterHandle = ?, localMemory = ?, rssSniperUrl = ?, telegramBotToken = ?, telegramChatId = ?, discordWebhookUrl = ?, whatsappApiUrl = ?, whatsappGroupId = ?, isActive = ?, postIntervalHours = ?
      WHERE blogId = ?
    `);
    
    const result = await stmt.run(youtubeChannelId || '', instagramHandle || '', twitterHandle || '', localMemory || '', rssSniperUrl || '', telegramBotToken || '', telegramChatId || '', discordWebhookUrl || '', whatsappApiUrl || '', whatsappGroupId || '', activeInt, postIntervalHours ?? 4, blogId);

    // Se não atualizou nada, significa que não tinha a linha.
    if (result.changes === 0) {
      await db.prepare(`INSERT INTO AgentConfig (id, blogId, youtubeChannelId, instagramHandle, twitterHandle, localMemory, rssSniperUrl, telegramBotToken, telegramChatId, discordWebhookUrl, whatsappApiUrl, whatsappGroupId, isActive, postIntervalHours) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(crypto.randomUUID(), blogId, youtubeChannelId || '', instagramHandle || '', twitterHandle || '', localMemory || '', rssSniperUrl || '', telegramBotToken || '', telegramChatId || '', discordWebhookUrl || '', whatsappApiUrl || '', whatsappGroupId || '', activeInt, postIntervalHours ?? 4);
    }

    // Salva Variáveis Visuais no Blog
    if (primaryColor !== undefined) {
      await db.prepare(`UPDATE Blog SET primaryColor = ?, secondaryColor = ?, layoutStyle = ? WHERE id = ?`).run(primaryColor, secondaryColor, layoutStyle, blogId);
    }

    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
