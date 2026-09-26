const fs = require('fs');
const path = require('path');
const Database = require('better-sqlite3');

// Tenta carregar .env localmente
require('dotenv').config({ path: path.resolve(process.cwd(), '.env') });

const DB_PATH = path.resolve(process.cwd(), 'dev.db');

/**
 * Fatiador Inteligente de Threads
 * Divide um texto longo em múltiplos blocos de até 270 caracteres (para sobrar espaço pro contador)
 */
function createThreadChunks(text, maxLength = 265) {
  const paragraphs = text.split('\n\n');
  const chunks = [];
  let currentChunk = '';

  for (const p of paragraphs) {
    if ((currentChunk + '\n\n' + p).length <= maxLength) {
      currentChunk += (currentChunk ? '\n\n' : '') + p;
    } else {
      if (currentChunk) chunks.push(currentChunk);
      
      // Se um parágrafo único for maior que o limite, quebra no espaço
      if (p.length > maxLength) {
         let remaining = p;
         while (remaining.length > 0) {
            if (remaining.length <= maxLength) {
               currentChunk = remaining;
               remaining = '';
            } else {
               let sliceIdx = remaining.lastIndexOf(' ', maxLength);
               if (sliceIdx === -1) sliceIdx = maxLength;
               chunks.push(remaining.substring(0, sliceIdx));
               remaining = remaining.substring(sliceIdx).trim();
            }
         }
      } else {
         currentChunk = p;
      }
    }
  }
  if (currentChunk) chunks.push(currentChunk);
  
  // Formatação Thread do Twitter (1/X)
  return chunks.map((c, i) => {
    if (chunks.length === 1) return c;
    if (i === chunks.length - 1) return c + ' 🏁';
    return c + ` 🧵 (${i+1}/${chunks.length})`;
  });
}

/**
 * Motor Central do Agente Twitter
 */
async function processTwitterQueue() {
  const db = new Database(DB_PATH);
  
  console.log('[TWITTER-BOT] 🐦 Buscando Threads Magnéticas na fila...');
  
  // Pegamos um Snippet do Twitter não publicado
  // OBS: Em bancos antigos, isPublished pode vir como NULL, então checamos IFNULL
  const task = await db.prepare(`
    SELECT * 
    FROM SocialSnippet 
    WHERE platform = 'twitter' AND IFNULL(isPublished, 0) = 0
    LIMIT 1
  `).get();

  if (!task) {
    console.log('[TWITTER-BOT] 💤 Nenhuma thread pendente.');
    return;
  }

  console.log(`[TWITTER-BOT] 🚀 Processando Thread do Post ID: ${task.postId}`);

  const apiKey = process.env.TWITTER_API_KEY;
  const apiSecret = process.env.TWITTER_API_SECRET;
  const accessToken = process.env.TWITTER_ACCESS_TOKEN;
  const accessSecret = process.env.TWITTER_ACCESS_SECRET;

  const chunks = createThreadChunks(task.content);
  console.log(`[TWITTER-BOT] 🧵 Texto fatiado em ${chunks.length} tweets.`);
  chunks.forEach((c, idx) => console.log(`   └ Tweet ${idx+1}: ${c.substring(0, 50)}... [${c.length} chars]`));

  if (!apiKey || !apiSecret || !accessToken || !accessSecret) {
    console.log(`[TWITTER-BOT] ⚠️ API Keys do Twitter ausentes no .env.`);
    console.log(`[TWITTER-BOT] ⚠️ Simulação de publicação realizada com sucesso.`);
    // Marca como publicado mesmo na simulação para não travar a fila
    await db.prepare(`UPDATE SocialSnippet SET isPublished = 1 WHERE id = ?`).run(task.id);
    return;
  }

  try {
    const { TwitterApi } = require('twitter-api-v2');
    const twitterClient = new TwitterApi({
      appKey: apiKey,
      appSecret: apiSecret,
      accessToken: accessToken,
      accessSecret: accessSecret,
    });

    // Envio real da Thread
    const rwClient = twitterClient.readWrite;
    const tweets = chunks.map(c => ({ text: c }));
    
    console.log('[TWITTER-BOT] 📡 Transmitindo Thread para os servidores do X.com...');
    await rwClient.v2.tweetThread(tweets);
    
    console.log('[TWITTER-BOT] ✅ Thread Publicada Oficialmente!');
    await db.prepare(`UPDATE SocialSnippet SET isPublished = 1 WHERE id = ?`).run(task.id);
  } catch (error) {
    console.error(`[TWITTER-BOT] 🚨 Falha na API do Twitter:`, error.message);
    if (error.data) console.error(error.data);
  }
}

if (require.main === module) {
  processTwitterQueue().then(() => {
    console.log('[TWITTER-BOT] Execução finalizada.');
  });
}

module.exports = { processTwitterQueue };
