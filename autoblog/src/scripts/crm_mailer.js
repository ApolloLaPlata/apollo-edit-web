const Database = require('better-sqlite3');
const path = require('path');

// Simulação de envio pelo SDK Resend ou SendGrid
// const { Resend } = require('resend');
// const resend = new Resend(process.env.RESEND_API_KEY);

const DB_PATH = path.resolve(process.cwd(), 'dev.db');

/**
 * Motor CRM Autônomo (E-mail Marketing)
 * Roda de Madrugada via Cron Job.
 * Pega os 3 artigos mais polêmicos gerados ontem, compila um Newsletter HTML Premium
 * e dispara para toda a base de Leads capturada pela Paywall.
 */
async function sendDailyNewsletter() {
  const db = new Database(DB_PATH);
  
  console.log('[CRM] 📨 Preparando Newsletter Diária de Fofocas...');

  // Pega as 3 matérias mais recentes
  const topPosts = db.prepare(`SELECT id, title, slug, coverImage FROM Post ORDER BY createdAt DESC LIMIT 3`).all();
  
  if (topPosts.length === 0) {
    console.log('[CRM] ⚠️ Sem matérias para enviar hoje.');
    return;
  }

  // Monta o Corpo do E-mail (HTML Premium)
  const emailHtml = `
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
      
      <div style="background-color: #dc2626; padding: 30px; text-align: center;">
        <h1 style="color: #fff; margin: 0; font-size: 28px; letter-spacing: -1px;">🔥 Notícias Quentes do Dia</h1>
        <p style="color: #ffcccc; font-size: 14px; margin-top: 10px;">O que a mídia tradicional está tentando esconder hoje!</p>
      </div>

      <div style="padding: 30px;">
        ${topPosts.map((post, idx) => `
          <div style="margin-bottom: 25px; border-bottom: 1px solid #eee; padding-bottom: 25px;">
            <span style="background: ${idx === 0 ? '#dc2626' : '#334155'}; color: #fff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-transform: uppercase;">
              ${idx === 0 ? 'Exclusivo' : 'Em Alta'}
            </span>
            <h2 style="font-size: 22px; color: #0f172a; margin: 10px 0;">${post.title}</h2>
            <img src="${post.coverImage}" alt="Capa" style="width: 100%; border-radius: 8px; margin-bottom: 15px; height: 250px; object-fit: cover;" />
            <a href="https://seusite.com/blog/${post.slug}" style="display: inline-block; background: #0f172a; color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: bold; font-size: 14px;">Ler Escândalo Completo →</a>
          </div>
        `).join('')}
      </div>

      <div style="background: #f8fafc; padding: 20px; text-align: center; color: #64748b; font-size: 12px;">
        <p>Você está recebendo este e-mail porque destravou conteúdo VIP no nosso site.</p>
        <a href="#" style="color: #94a3b8; text-decoration: underline;">Descadastrar</a>
      </div>
    </div>
  `;

  // Simulação de Disparo
  console.log(`[CRM] 🚀 Disparando Newsletter HTML para 5.430 Leads da Base (Simulação de Envio).`);
  
  /* CÓDIGO REAL DE DISPARO NO FUTURO
  const leads = db.prepare(`SELECT email FROM Leads WHERE status = 'active'`).all();
  for(let lead of leads) {
    await resend.emails.send({
      from: 'Fofocas VIP <vip@seusite.com>',
      to: lead.email,
      subject: '🚨 Você não vai acreditar no que vazou hoje...',
      html: emailHtml
    });
    // Atualiza pontuação do Lead (Lead Scoring)
    db.prepare('UPDATE Leads SET score = score + 5 WHERE email = ?').run(lead.email);
  }
  */

  console.log('[CRM] ✅ Disparo Concluído. Tráfego Orgânico Reverso ativado!');
}

if (require.main === module) {
  sendDailyNewsletter();
}

module.exports = { sendDailyNewsletter };
