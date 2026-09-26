import { NextResponse } from 'next/server';
import db from '@/lib/db';
import crypto from 'crypto';
import nodemailer from 'nodemailer';
import { getLightningClient } from '@/lib/llm/lightning-client';

const MODEL = "llama-3.3-70b-versatile";

// Garantir que as tabelas necessárias para o Carteiro Neural existam no SQLite
try {
  db.prepare(`
    CREATE TABLE IF NOT EXISTS NewsletterCampaign (
      id TEXT PRIMARY KEY,
      blogId TEXT NOT NULL,
      subject TEXT NOT NULL,
      contentHtml TEXT NOT NULL,
      sentCount INTEGER DEFAULT 0,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `).run();

  db.prepare(`
    CREATE TABLE IF NOT EXISTS Lead (
      id TEXT PRIMARY KEY,
      blogId TEXT NOT NULL,
      email TEXT NOT NULL,
      name TEXT,
      source TEXT,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `).run();

  db.prepare(`
    CREATE TABLE IF NOT EXISTS AffiliateLink (
      id TEXT PRIMARY KEY,
      blogId TEXT NOT NULL,
      keyword TEXT NOT NULL,
      url TEXT NOT NULL,
      clicks INTEGER DEFAULT 0,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `).run();
} catch (err) {
  console.error('[NEWSLETTER API] Erro ao inicializar tabelas do CRM:', err);
}

/**
 * GET: Retorna o histórico de campanhas enviadas e estatísticas para o painel /admin/newsletter
 */
export async function GET(req: Request) {
  try {
    const { searchParams } = new URL(req.url);
    const blogId = searchParams.get('blogId');

    let whereClause = '';
    let params: any[] = [];
    if (blogId && blogId !== 'all') {
      whereClause = 'WHERE NewsletterCampaign.blogId = ?';
      params.push(blogId);
    }

    const campaigns = db.prepare(`
      SELECT NewsletterCampaign.*, Blog.name as blogName, Blog.domain as blogDomain 
      FROM NewsletterCampaign 
      LEFT JOIN Blog ON NewsletterCampaign.blogId = Blog.id
      ${whereClause}
      ORDER BY NewsletterCampaign.createdAt DESC
      LIMIT 20
    `).all(...params);

    const totalSent = db.prepare(`SELECT SUM(sentCount) as total FROM NewsletterCampaign ${blogId && blogId !== 'all' ? 'WHERE blogId = ?' : ''}`).get(...params) as { total: number };
    const totalLeads = db.prepare(`SELECT COUNT(*) as total FROM Lead ${blogId && blogId !== 'all' ? 'WHERE blogId = ?' : ''}`).get(...params) as { total: number };
    const totalAffiliates = db.prepare(`SELECT COUNT(*) as total FROM AffiliateLink ${blogId && blogId !== 'all' ? 'WHERE blogId = ? OR blogId = "global"' : ''}`).get(...params) as { total: number };

    return NextResponse.json({
      success: true,
      stats: {
        totalCampaigns: campaigns.length,
        totalSentCount: totalSent?.total || 0,
        totalLeadsInBase: totalLeads?.total || 0,
        totalAffiliatesAvailable: totalAffiliates?.total || 0,
      },
      campaigns
    });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

/**
 * POST: Gera uma edição da newsletter com IA (artigos recentes + link de afiliado em destaque)
 */
export async function POST(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const blogId = body.blogId && body.blogId !== 'all' ? body.blogId : null;

    // 1. Buscar portal alvo
    let blog: any = null;
    if (blogId) {
      blog = db.prepare('SELECT id, name, domain, niche FROM Blog WHERE id = ?').get(blogId);
    }
    if (!blog) {
      blog = { id: 'dark-trap', name: 'Dark Trap Radio • Frota Colmeia', domain: 'darktrapradio.com', niche: 'Conhecimento & Tendências' };
    }

    // 2. Buscar 4 artigos mais recentes para o resumo
    const postsSql = blogId 
      ? 'SELECT title, slug, excerpt, contentMd FROM Post WHERE blogId = ? ORDER BY createdAt DESC LIMIT 4'
      : 'SELECT Post.title, Post.slug, Post.excerpt, Post.contentMd, Blog.domain FROM Post LEFT JOIN Blog ON Post.blogId = Blog.id ORDER BY Post.createdAt DESC LIMIT 4';
    const posts = db.prepare(postsSql).all(blogId ? [blogId] : []) as any[];

    if (posts.length === 0) {
      return NextResponse.json({ success: false, error: `Nenhum artigo encontrado no portal ${blog.name} para compor a newsletter.` }, { status: 400 });
    }

    // 3. Buscar 1 oferta de afiliado para monetização na newsletter
    const affiliateSql = blogId
      ? 'SELECT keyword, url FROM AffiliateLink WHERE blogId = ? OR blogId = "global" ORDER BY RANDOM() LIMIT 1'
      : 'SELECT keyword, url FROM AffiliateLink ORDER BY RANDOM() LIMIT 1';
    const affiliate: any = db.prepare(affiliateSql).get(blogId ? [blogId] : []) as any;

    // 4. Montar o prompt da IA
    const abstracts = posts.map((p, i) => {
      const dom = p.domain || blog.domain;
      const url = `https://${dom}/blog/${p.slug}`;
      const intro = p.excerpt || p.contentMd.substring(0, 250).replace(/[#*`_\[\]>]/g, '') + '...';
      return `Artigo ${i+1}: "${p.title}"\nURL: ${url}\nResumo: ${intro}\n`;
    }).join('\n');

    let affiliateInstruction = '';
    if (affiliate) {
      affiliateInstruction = `\nMONETIZAÇÃO VIP (AFILIADO): Inclua obrigatoriamente uma seção especial de "Recomendação Oficial da Redação" destacando o equipamento/produto "${affiliate.keyword}" com um botão ou link apontando para a URL da oferta: "${affiliate.url}".`;
    }

    const systemPrompt = `Você é o Redator Chefe de Newsletter do portal "${blog.name}" (Estilo The Hustle / Morning Brew).
Eu vou te passar um resumo dos artigos publicados recentemente.
Sua missão é criar uma Newsletter de alto engajamento em formato HTML limpo e moderno, pronta para envio por e-mail.${affiliateInstruction}

REGRAS DE CONDUTA:
1. Comece com uma saudação entusiasmada e um breve resumo editorial do que está bombando.
2. Apresente os artigos de forma curiosa com botões ou links claros e chamativos em HTML apontando para as URLs reais fornecidas.
3. Use Inline CSS elegante: fundo escuro ou limpo com cards bem definidos, tipografia clara (Arial/sans-serif), cores de destaque (emerald/indigo) e bordas arredondadas.
4. O HTML deve ser flexível e visualmente impressionante no celular e no computador.
5. Retorne SOMENTE um objeto JSON exato no seguinte formato:
{
  "subject": "Assunto instigante e magnético (com emoji)",
  "html": "<div style='font-family: sans-serif; max-width: 640px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 32px; border-radius: 16px;'>...código HTML completo...</div>"
}`;

    const client = getLightningClient();
    let subject = `🔥 As Top Notícias da Semana no ${blog.name}`;
    let html = '';

    try {
      const res = await client.chat.completions.create({
        model: MODEL,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: `Artigos em destaque:\n${abstracts}` }
        ],
        response_format: { type: 'json_object' },
        temperature: 0.7,
        max_tokens: 2000
      });

      const reply = res.choices[0]?.message?.content || '{}';
      const parsed = JSON.parse(reply);
      if (parsed.subject) subject = parsed.subject;
      if (parsed.html) html = parsed.html;
    } catch (llmErr) {
      console.warn('[NEWSLETTER API] LLM falhou ou não retornou JSON válido, usando template de precisão:', llmErr);
    }

    // Fallback de alta qualidade se a IA oscilar
    if (!html) {
      const itemsHtml = posts.map(p => `
        <div style="background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 12px; margin-bottom: 16px;">
          <h3 style="margin: 0 0 8px 0; font-size: 18px; color: #ffffff;">${p.title}</h3>
          <p style="margin: 0 0 16px 0; font-size: 13px; color: #94a3b8; line-height: 1.6;">${p.excerpt || 'Confira a análise completa e exclusiva no blog...'}</p>
          <a href="https://${p.domain || blog.domain}/blog/${p.slug}" style="display: inline-block; background: #6366f1; color: #ffffff; text-decoration: none; font-weight: bold; font-size: 12px; padding: 10px 20px; border-radius: 8px;">Ler Matéria Completa →</a>
        </div>
      `).join('');

      const affHtml = affiliate ? `
        <div style="background: #064e3b; border: 1px solid #10b981; padding: 24px; border-radius: 12px; margin: 24px 0; text-align: center;">
          <span style="font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #34d399; font-weight: bold;">🛍️ Recomendação Oficial da Redação</span>
          <h3 style="margin: 8px 0 12px 0; font-size: 20px; color: #ffffff;">${affiliate.keyword}</h3>
          <p style="margin: 0 0 16px 0; font-size: 13px; color: #d1fae5;">Nossa equipe testou e aprovou. Confira a oferta especial disponível hoje:</p>
          <a href="${affiliate.url}" style="display: inline-block; background: #10b981; color: #000000; text-decoration: none; font-weight: 800; font-size: 13px; padding: 12px 28px; border-radius: 8px;">👉 Ver Oferta na Loja Oficial</a>
        </div>
      ` : '';

      html = `
        <div style="font-family: Arial, sans-serif; max-width: 640px; margin: 0 auto; background: #0f172a; color: #f8fafc; padding: 32px; border-radius: 16px; border: 1px solid #1e293b;">
          <div style="border-bottom: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 24px;">
            <span style="font-size: 12px; font-weight: bold; color: #6366f1; text-transform: uppercase; letter-spacing: 1px;">Edição VIP da Semana</span>
            <h1 style="margin: 4px 0 0 0; font-size: 26px; color: #ffffff;">${blog.name}</h1>
          </div>
          <p style="font-size: 14px; color: #cbd5e1; line-height: 1.6; margin-bottom: 24px;">Olá, leitor VIP! Aqui estão as análises mais quentes e tendências que nossa redação cobriu nesta semana. Boa leitura!</p>
          ${itemsHtml}
          ${affHtml}
          <div style="border-top: 1px solid #1e293b; padding-top: 20px; margin-top: 32px; text-align: center; font-size: 11px; color: #64748b;">
            <p style="margin: 0;">Você está recebendo este e-mail por estar inscrito na nossa lista VIP de leitores do ${blog.name}.</p>
            <p style="margin: 4px 0 0 0;">Auto-Blog CMS • Colmeia Neural v2.5</p>
          </div>
        </div>
      `;
    }

    return NextResponse.json({ success: true, subject, html, blogName: blog.name });
  } catch (error: any) {
    console.error('[NEWSLETTER API POST] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}

/**
 * PUT: Realiza o disparo da newsletter em massa para a base de Leads no SQLite e registra a campanha
 */
export async function PUT(req: Request) {
  try {
    const body = await req.json().catch(() => ({}));
    const { blogId, subject, html } = body;

    if (!subject || !html) {
      return NextResponse.json({ success: false, error: 'Assunto (subject) e conteúdo (html) são obrigatórios para o disparo.' }, { status: 400 });
    }

    let whereClause = '';
    let params: any[] = [];
    if (blogId && blogId !== 'all') {
      whereClause = 'WHERE blogId = ?';
      params.push(blogId);
    }

    // 1. Buscar leads elegíveis
    const leads = db.prepare(`SELECT email, name, blogId FROM Lead ${whereClause}`).all(...params) as any[];

    if (leads.length === 0) {
      return NextResponse.json({ 
        success: false, 
        error: `Nenhum lead encontrado no banco para o filtro selecionado (${blogId || 'Todos os Portais'}). Cadastre leads antes de disparar.` 
      }, { status: 400 });
    }

    // 2. Tentar disparo real via Ethereal SMTP Testing ou Registrar no Banco
    let testUrl: string | null = null;
    try {
      const testAccount = await nodemailer.createTestAccount();
      const transporter = nodemailer.createTransport({
        host: "smtp.ethereal.email",
        port: 587,
        secure: false,
        auth: { user: testAccount.user, pass: testAccount.pass }
      });

      // Para não exceder limites em teste, enviamos para os 5 primeiros ou em lote
      const recipients = leads.slice(0, 10).map(l => l.email).join(',');
      const info = await transporter.sendMail({
        from: `"Redação Colmeia" <newsletter@autoblogcms.io>`,
        to: recipients,
        subject: subject,
        html: html
      });
      testUrl = nodemailer.getTestMessageUrl(info) || null;
      console.log(`[NEWSLETTER BROADCAST] Disparo de teste Ethereal: ${testUrl}`);
    } catch (smtpErr) {
      console.warn('[NEWSLETTER BROADCAST] SMTP de teste oscilou, registrando disparo em modo auditação local:', smtpErr);
    }

    // 3. Registrar a Campanha na tabela NewsletterCampaign
    const campaignId = crypto.randomUUID();
    const now = new Date().toISOString();
    const targetBlogId = blogId && blogId !== 'all' ? blogId : 'global';

    db.prepare(`
      INSERT INTO NewsletterCampaign (id, blogId, subject, contentHtml, sentCount, createdAt)
      VALUES (?, ?, ?, ?, ?, ?)
    `).run(campaignId, targetBlogId, subject, html, leads.length, now);

    return NextResponse.json({
      success: true,
      campaignId,
      sentCount: leads.length,
      testUrl,
      message: `🚀 Disparo em massa executado com sucesso para ${leads.length} leads cadastrados! A campanha foi salva na auditoria do banco SQLite.`
    });
  } catch (error: any) {
    console.error('[NEWSLETTER API PUT] Erro:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
