const Parser = require('rss-parser');
const sqlite3 = require('better-sqlite3');
const path = require('path');
const parser = new Parser();

const dbPath = path.resolve(__dirname, '../../dev.db');
const db = new sqlite3(dbPath);

// Google Trends RSS para o Brasil (pt-BR) - Assuntos mais pesquisados do dia
const TRENDS_URL = 'https://trends.google.com/trends/trendingsearches/daily/rss?geo=BR';

// Webhook mocado do Apollo Edit Web (Destino Fase 4)
const APOLLO_WEBHOOK_URL = process.env.APOLLO_INGEST_URL || 'http://localhost:3000/api/apollo/ingest';

async function huntTrends() {
  console.log('🐺 [HYPE-SCOUT] Farejando tendências no Google Trends...');

  try {
    let feed = { items: [] };
    try {
      feed = await parser.parseURL(TRENDS_URL);
    } catch (e) {
      console.log('⚠️ RSS do Google Trends bloqueou a leitura (404/429). Usando Mock de Teste...');
      feed.items = [
        { title: 'Inteligência Artificial toma conta do mercado', 'ht:approx_traffic': '500K+', link: 'https://news.google.com' },
        { title: 'Vazamento da nova RTX 5090', 'ht:approx_traffic': '1M+', link: 'https://news.google.com' }
      ];
    }
    
    // Pega as 3 tendências mais quentes do momento
    const topTrends = feed.items.slice(0, 3);
    
    for (const trend of topTrends) {
      const keyword = trend.title;
      const searchVolume = trend['ht:approx_traffic'] || '10K+';
      const newsUrl = trend['ht:news_item'] ? trend['ht:news_item'][0]['ht:news_item_url'][0] : trend.link;

      console.log(`🔥 [HYPE DETECTADO]: ${keyword} (${searchVolume} buscas)`);

      // 1. Verifica se já não escrevemos sobre isso hoje
      const existing = await db.prepare('SELECT id FROM Post WHERE title LIKE ?').get(`%${keyword}%`);
      if (existing) {
         console.log(`⚠️ Já cobrimos "${keyword}". Pulando...`);
         continue;
      }

      console.log(`✍️ [HYPE-SCOUT] Gerando artigo sobre: ${keyword}`);
      
      // FASE 106: LLM Personas (Ghostwriters)
      // Carrega o banco de personas e escolhe uma aleatoriamente para não deixar o blog robótico
      const personasData = require('./personas.json');
      const randomPersona = personasData.personas[Math.floor(Math.random() * personasData.personas.length)];
      
      console.log(`🎭 [GHOSTWRITER] Persona Ativada: ${randomPersona.name} (${randomPersona.authorName})`);

      const postSlug = keyword.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      
      const insertPost = db.prepare(`
        INSERT INTO Post (id, blogId, title, slug, contentMd, contentHtml, isPublished, author, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
      `);

      // BlogID padrão (Ajustar para pegar o primeiro blog ativo)
      const firstBlog = await db.prepare('SELECT id FROM Blog LIMIT 1').get();
      if(!firstBlog) {
          console.log('🚨 Nenhum blog encontrado no Banco. Crie um blog primeiro.');
          return;
      }

      const postId = `hype_${Date.now()}_${Math.floor(Math.random()*1000)}`;
      
      // Simulação da Geração da IA usando o Style Template da Persona
      // Na versão final com GROQ, injetaremos o "randomPersona.prompt" no SystemMessage do LLM.
      let fakeContent = randomPersona.styleTemplate
          .replace(/{keyword}/g, keyword)
          .replace(/{searchVolume}/g, searchVolume);
          
      // FASE 113: DETECÇÃO DE YMYL (Your Money or Your Life) E QUARENTENA
      const ymylKeywords = ['cripto', 'bitcoin', 'dinheiro', 'investimento', 'saúde', 'doença', 'morte', 'golpe', 'crime'];
      const isYMYL = ymylKeywords.some(k => keyword.toLowerCase().includes(k) || randomPersona.id === 'crypto');
      const publishStatus = isYMYL ? 2 : 1;
      
      if (isYMYL) {
         console.log(`🛡️ [QUARENTENA] Assunto sensível detectado. Enviando para Revisão Humana (isPublished=2)`);
      }

      // FASE 106: Inserindo post com a assinatura (author) da Persona Específica e com Fila de Quarentena (Fase 113)
      insertPost.run(postId, firstBlog.id, `${keyword} explode na internet: Entenda tudo`, postSlug, fakeContent, fakeContent, publishStatus, randomPersona.authorName);
      
      if (publishStatus === 1) {
         console.log(`✅ Post Publicado [${randomPersona.id}]: /p/${postSlug}`);
      } else {
         console.log(`⏳ Post Retido para Revisão [${randomPersona.id}]: ${keyword}`);
      }

      // 3. Disparar Webhook URGENTE para o Apollo Edit Web (Maestro)
      console.log(`🚀 [HYPE-SCOUT] Disparando Webhook de Urgência para o Apollo Edit Web...`);
      
      try {
        // Simulando o disparo (fetch nativo no Node v18+)
        /*
        await fetch(APOLLO_WEBHOOK_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                trigger: 'HYPE_SCOUT',
                keyword: keyword,
                contextUrl: newsUrl,
                postSlug: postSlug,
                urgency: 'HIGH',
                message: 'GERE UM VÍDEO SOBRE ISSO IMEDIATAMENTE'
            })
        });
        */
        console.log(`🎯 [APOLLO-SYNC] Sinal enviado para a Nave-Mãe. O Vídeo será gerado. (Simulado)`);
      } catch (err) {
        console.log(`❌ [APOLLO-SYNC] Erro ao comunicar com Apollo: ${err.message}`);
      }
    }
  } catch (error) {
    console.error('❌ [HYPE-SCOUT] Erro ao farejar trends:', error.message);
  }
}

// Executar direto
huntTrends();
