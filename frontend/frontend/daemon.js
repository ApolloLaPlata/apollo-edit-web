// Node.js 18+ tem fetch nativo - sem necessidade de node-fetch
const { processQueue } = require('./src/scripts/video_maker.js');
const { processSocialQueue } = require('./src/scripts/social_publisher.js');

const CMS_URL = 'http://localhost:3000';
const CRON_INTERVAL_MS = 60 * 1000; // Tick da redação (1 min)
const NEWSLETTER_INTERVAL_MS = 1000 * 60 * 60 * 24 * 7; // Disparo de Newsletter (1 Semana - Sexta-Feira Ideal)

// 1. Motor de Redação de Notícias (Aranha Web)
async function triggerTick() {
  console.log(`\n[DAEMON] ⏰ Motor de Redação (Tick): ${new Date().toLocaleString()}`);
  try {
    const response = await fetch(`${CMS_URL}/api/admin/engine/tick`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    const data = await response.json();
    if (data.success && data.message) console.log(`[DAEMON] ✅ ${data.message}`);
    else if (data.success === false) console.error(`[DAEMON] ❌ Erro: ${data.error}`);
  } catch (error) {
    console.error(`[DAEMON] ❌ Falha de Conexão com o CMS (Servidor offline)`);
  }
}

// 2. Motor do Carteiro Neural (Produção Autônoma da Newsletter)
async function triggerNewsletter() {
  console.log(`\n[DAEMON - NEWSLETTER] 📧 Iniciando a Máquina de Disparo (Auto-Geração)...`);
  try {
    // 1. Pede para a Inteligência Artificial produzir a Newsletter (Resumo + Afiliados)
    const genRes = await fetch(`${CMS_URL}/api/admin/newsletter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blogId: 'all' }) // Varre e envia da frota Global
    });
    
    const genData = await genRes.json();
    
    if (genData.success && genData.subject && genData.html) {
      console.log(`[DAEMON - NEWSLETTER] ✅ Edição escrita pela IA! Assunto: "${genData.subject}"`);
      
      // 2. Confirma o Disparo em Massa (SMTP / Salva no Banco)
      console.log(`[DAEMON - NEWSLETTER] 🚀 Iniciando Disparo para a base de Leads VIP...`);
      const sendRes = await fetch(`${CMS_URL}/api/admin/newsletter`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          blogId: 'all',
          subject: genData.subject,
          html: genData.html
        })
      });

      const sendData = await sendRes.json();
      if (sendData.success) {
        console.log(`[DAEMON - NEWSLETTER] 🎯 Sucesso Absoluto! E-mails enviados. ${sendData.message}`);
      } else {
        console.error(`[DAEMON - NEWSLETTER] ❌ Erro no Disparo: ${sendData.error}`);
      }
    } else {
      console.error(`[DAEMON - NEWSLETTER] ❌ Falha da I.A ao gerar HTML: ${genData.error}`);
    }
  } catch (error) {
    console.error(`[DAEMON - NEWSLETTER] ❌ Falha de Conexão com o CMS (Newsletter Engine)`);
  }
}

console.log(`
      🤖 AUTO-BLOG CMS DAEMON INICIADO 🤖
    - Motor de Notícias (Tick): A cada 1 Minuto
    - Produção de Newsletter: A cada 7 Dias (Semanal)
    - Conectado em: ${CMS_URL}
`);

// O Daemon aguardará o primeiro ciclo do relógio para agir.
// Não dispara redação de Notícias imediatamente no boot para evitar consumo descontrolado em testes de UI.
setInterval(triggerTick, CRON_INTERVAL_MS);

// Agenda a Newsletter para 7 dias, mas no seu ambiente real você pode disparar imediatamente
// triggerNewsletter();
setInterval(triggerNewsletter, NEWSLETTER_INTERVAL_MS);

// 3. Motor de Renderização de Vídeo (Hub de Shorts) e Motor de Postagem
// Checa a cada 30 segundos se há novos roteiros pendentes para virar vídeo
setInterval(async () => {
  try {
    await processQueue();
    // Após tentar renderizar o vídeo, o robô verifica se tem algum vídeo pronto para a Fase 7 (Distribuição)
    await processSocialQueue();
  } catch (err) {
    // Fail silently in daemon to not crash
  }
}, 30 * 1000);
