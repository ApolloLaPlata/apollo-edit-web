import { NextResponse } from 'next/server';
import db from '@/lib/db';
import { executeSwarmPipeline } from '@/lib/agents/swarm';
import { runOmniScraper } from '@/lib/agents/omni_scraper';
import { runDailyNewsletter } from '@/lib/agents/newsletter';
import { runOracleAgent } from '@/lib/agents/oracle';
import { runSocialAgent } from '@/lib/agents/social';
import { runMaintenanceBot } from '@/lib/agents/maintenance';
import { checkYouTubeChannels } from '@/lib/agents/youtube';
import { runSniperAgent } from '@/lib/agents/sniper';
import { runBackupAgent } from '@/lib/agents/backup';
import { executeAutonomousEditorialCycle } from '@/lib/agents/autonomous_engine';
import { executeFullSynapseCycle } from '@/lib/agents/synapse_engine';
import { executeFullImmuneCycle } from '@/lib/agents/immune_engine';
import { executeFullGenesisCycle } from '@/lib/agents/genesis_engine';
import { executeFullEndocrineCycle } from '@/lib/agents/endocrine_engine';
import { executeFullCrossChannelCycle } from '@/lib/agents/crosschannel_engine';
import { executeFullTrendCycle } from '@/lib/agents/trend_engine';
import { executeFullSeoHealerCycle } from '@/lib/agents/seo_healer_engine';

// Rate Limit em Memória para bloquear DDoS no Cron
const requestLog = new Map<string, number>();

// Essa rota é chamada pelo daemon.js a cada minuto.
export async function POST(req: Request) {
  try {
    const ip = req.headers.get('x-forwarded-for') || '127.0.0.1';
    const nowStamp = Date.now();
    const lastRequest = requestLog.get(ip);
    
    if (lastRequest && (nowStamp - lastRequest) < 45000) {
       // Se o mesmo IP bater no cron antes de 45 segundos, bloqueia (Rate Limit)
       return NextResponse.json({ success: false, error: 'Rate Limit: Many requests.' }, { status: 429 });
    }
    requestLog.set(ip, nowStamp);

    // 0. Varredura Total das Redes Sociais
    await runOmniScraper();
    
    // 0.1 RSS Sniper (News Jacking - Dispara aleatoriamente para evitar bans e lentidão)
    if (Math.random() < 0.15) {
      await runSniperAgent();
    }
    
    // 0.3 Varredura de Canais do YouTube (Omni-Channel Sync)
    // Roda a cada 5 minutos (Math.random para espalhar a carga e não tomar block do YouTube)
    if (Math.random() < 0.20) {
      await checkYouTubeChannels();
    }

    // 0.4 CÉREBRO EDITORIAL AUTÔNOMO (AUTOGESTÃO & REPOSTAGEM DE MÍDIA)
    if (Math.random() < 0.25) {
      await executeAutonomousEditorialCycle();
    }

    // 0.45 SISTEMA NERVOSO DA COLMEIA (SINAPSES DE SEO, OTIMIZAÇÃO A/B DE TÍTULOS & MEGAFONE)
    if (Math.random() < 0.20) {
      await executeFullSynapseCycle();
    }

    // 0.48 SISTEMA IMUNOLÓGICO DA COLMEIA (REGENERADOR DE TECIDOS EDITORIAL & AUTO-ADAPTAÇÃO)
    if (Math.random() < 0.15) {
      await executeFullImmuneCycle();
    }

    // 0.49 SISTEMA DE GÊNESE TERRITORIAL E MONETIZAÇÃO DA COLMEIA (AUTO-EXPANSÃO DE NICHOS)
    if (Math.random() < 0.10) {
      await executeFullGenesisCycle();
    }

    // 0.495 SISTEMA ENDÓCRINO DA COLMEIA (HOMEOSTASE HORMONAL, FACT-CHECKING E VIRAL BOOST)
    if (Math.random() < 0.12) {
      await executeFullEndocrineCycle();
    }

    // 0.497 TELEMETRIA CROSS-CHANNEL (RADAR DE 8 REDES SOCIAIS + INTELIGÊNCIA ESTRATÉGICA)
    if (Math.random() < 0.08) {
      await executeFullCrossChannelCycle();
    }

    // 0.498 ORÁCULO DE TENDÊNCIAS (FASE 138 - AGENDA PAUTAS PREDITIVAS)
    if (Math.random() < 0.07) {
      await executeFullTrendCycle();
    }

    // 0.499 AUTO-HEALER DE SEO ON-PAGE (FASE 139 - ZELADOR DE METADADOS)
    if (Math.random() < 0.09) {
      await executeFullSeoHealerCycle();
    }
    
    // 0.5 Carteiro Neural (Relógio 24h)
    await runDailyNewsletter();

    // =============================================
    // FASE 65: ROBÔ ZELADOR E CAIXA PRETA (Manutenção Diária 3:00 AM)
    // =============================================
    const now = new Date();
    if (now.getHours() === 3 && now.getMinutes() === 0) {
      await runMaintenanceBot();
      await runBackupAgent();
    }

    // =============================================
    // FASE 63: ROBÔ DIRETOR E FASE 77: AGENTE SOCIAL
    // =============================================
    const blogs = await db.prepare('SELECT id, name FROM Blog').all() as any[];
    for (const blog of blogs) {
      const queueCount = await db.prepare(`SELECT COUNT(*) as c FROM ContentQueue WHERE blogId = ? AND status = 'pending'`).get(blog.id) as any;
      if (queueCount.c === 0) {
        // console.log(`[ROBÔ DIRETOR] Fila do canal ${blog.name} está VAZIA. Acordando o Oráculo...`);
        await runOracleAgent(blog.id); 
      }
      
      // Acorda o Agente Social para disparar iscas de tráfego
      await runSocialAgent(blog.id);
    }

    // =============================================
    // FASE 64: SELF-HEALING (Auto-cura de Pautas)
    // =============================================
    // Se alguma pauta ficou travada em 'writing' por mais de 1 hora (crash da IA), volta para 'pending'
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000).toISOString();
    const healed = await db.prepare(`UPDATE ContentQueue SET status = 'pending' WHERE status = 'writing' AND createdAt < ?`).run(oneHourAgo);
    if (healed.changes > 0) {
      console.log(`[SELF-HEALING] 🩺 ${healed.changes} pautas travadas foram destravadas e voltaram para a fila.`);
    }

    // =============================================
    // FASE 64: ENGAJAMENTO FANTASMA 24/7
    // =============================================
    // 10% de chance a cada minuto de um "Fantasma" ler e comentar num post recém-lançado
    if (Math.random() < 0.10) {
       try {
         // Chamada interna local
         await fetch('http://localhost:3000/api/cron/simulate-comments?token=secret-cron');
       } catch (e) {
         // Silenced error
       }
    }

    // 1. Procura na Fila de Pautas (ContentQueue) alguma pauta pendente
    //    com verificação de Drip-Feed por canal
    const pendingTask = await db.prepare(`SELECT * FROM ContentQueue WHERE status = 'pending' ORDER BY createdAt ASC LIMIT 1`).get() as any;

    if (!pendingTask) {
      return NextResponse.json({ success: true, message: 'Nenhuma pauta na fila.' });
    }

    // =============================================
    // FASE 36: MÁQUINA DO TEMPO (DRIP-FEED CHECK)
    // =============================================
    const agentCfg = await db.prepare(`SELECT postIntervalHours FROM AgentConfig WHERE blogId = ?`).get(pendingTask.blogId) as any;
    const intervalHours = agentCfg?.postIntervalHours ?? 4;
    
    // Último post publicado deste canal
    const lastPost = await db.prepare(`SELECT createdAt FROM Post WHERE blogId = ? ORDER BY createdAt DESC LIMIT 1`).get(pendingTask.blogId) as any;
    
    if (lastPost) {
      const lastPostTime = new Date(lastPost.createdAt).getTime();
      const nowTime = Date.now();
      const diffHours = (nowTime - lastPostTime) / (1000 * 60 * 60);
      
      if (diffHours < intervalHours) {
        const remaining = (intervalHours - diffHours).toFixed(1);
        return NextResponse.json({ 
          success: true, 
          message: `[DRIP-FEED] Canal ${pendingTask.blogId}: próxima postagem em ${remaining}h (intervalo: ${intervalHours}h).` 
        });
      }
    }

    // Marca como 'writing' para evitar execuções simultâneas
    await db.prepare(`UPDATE ContentQueue SET status = 'writing' WHERE id = ?`).run(pendingTask.id);

    // Pega o prompt/persona do Blog correspondente
    const blog = await db.prepare(`SELECT * FROM Blog WHERE id = ?`).get(pendingTask.blogId) as any;
    if (!blog) {
      await db.prepare(`UPDATE ContentQueue SET status = 'error' WHERE id = ?`).run(pendingTask.id);
      return NextResponse.json({ success: false, error: 'Blog da pauta não encontrado.' });
    }

    // Dispara o Enxame Assincronamente (Não damos await para não segurar o request e dar timeout)
    executeSwarmPipeline(pendingTask.topic, blog.id, blog.personaPrompt)
      .then(async () => {
        await db.prepare(`UPDATE ContentQueue SET status = 'published' WHERE id = ?`).run(pendingTask.id);
        console.log(`[TICK] Pauta "${pendingTask.topic}" concluída com sucesso!`);
      })
      .catch(async err => {
        await db.prepare(`UPDATE ContentQueue SET status = 'pending' WHERE id = ?`).run(pendingTask.id);
        console.error(`[TICK] Erro ao executar pauta:`, err);
      });

    return NextResponse.json({ 
      success: true, 
      message: `Enxame iniciado para a pauta: "${pendingTask.topic}"`
    });

  } catch (error: any) {
    console.error('[ENGINE TICK] Error:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
