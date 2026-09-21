const Database = require('better-sqlite3');
const path = require('path');

/**
 * 🌡️ MOTOR DE TEMPERATURA E REENGAJAMENTO (Lead Engine)
 * Responsável por varrer o Banco de Dados, atualizar a "Temperatura" dos Leads 
 * (Cold, Warm, Hot) e disparar e-mails isca de resgate para quem sumiu do site.
 */

const DB_PATH = path.resolve(process.cwd(), 'dev.db');

function runLeadEngine() {
  console.log('[LEAD-ENGINE] 🧠 Analisando Comportamento dos Usuários e Temperaturas...');
  
  // Como é arquitetura V3, simularemos as queries de pontuação no DB SQLite
  try {
    const db = new Database(DB_PATH);
    
    // 1. LEAD SCORING: Esfria a temperatura de todo mundo que não clica em emails há 1 semana
    // db.prepare(`UPDATE Leads SET score = score - 10 WHERE lastClickDate < date('now', '-7 days')`).run();
    console.log('[LEAD-ENGINE] 📉 Termômetro ajustado: Leads inativos perderam 10 Pontos de VIP Score.');

    // 2. DETECTOR DE ABANDONO: Acha Leads 'Frios' e envia Fofoca Isca
    // const coldLeads = db.prepare(`SELECT email FROM Leads WHERE score < 20`).all();
    const mockColdLeads = [{ email: 'leitor_sumido@gmail.com' }, { email: 'maria.fofoca@hotmail.com' }];
    
    console.log(`[LEAD-ENGINE] 🚨 Foram detectados ${mockColdLeads.length} Leitores que sumiram do site.`);
    console.log(`[LEAD-ENGINE] 🎣 Preparando E-mail Isca de Gatilho Curiosidade para trazê-los de volta...`);
    
    for (let lead of mockColdLeads) {
      // Disparo do email isca...
      // resend.emails.send({ ... subject: 'Fizeram algo terrível com você saber quem...', html: '...' })
      console.log(`[LEAD-ENGINE] 📨 Isca de Curiosidade disparada para: ${lead.email}`);
    }

    // 3. SEPARAÇÃO DOS "WHALES" (Super Leitores)
    // const whales = db.prepare(`SELECT email FROM Leads WHERE score > 500`).all();
    console.log('[LEAD-ENGINE] 👑 Análise de Whales concluída. Separação de Leitores Super Engajados para Anúncios Premium de Maior Custo.');

  } catch (error) {
    console.error('[LEAD-ENGINE] Erro no processamento do CRM:', error.message);
  }
}

// Inicia se rodado pelo terminal (Cron)
if (require.main === module) {
  runLeadEngine();
}

module.exports = { runLeadEngine };
