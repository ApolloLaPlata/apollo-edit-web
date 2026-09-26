const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');
const ffmpeg = require('fluent-ffmpeg');
const ffmpegStatic = require('ffmpeg-static');
const googleTTS = require('google-tts-api');
const { generateSrt } = require('./subtitle_generator');

// Configura o fluent-ffmpeg para usar o binário estático baixado via npm
ffmpeg.setFfmpegPath(ffmpegStatic);

const DB_PATH = path.resolve(process.cwd(), 'dev.db');
const UPLOADS_DIR = path.resolve(process.cwd(), 'public/uploads/videos');

// Garante que o diretório de vídeos exista
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true });
}

/**
 * Gera um arquivo de áudio temporário MP3 a partir de texto usando TTS Gratuito
 */
async function generateTTS(text, outputPath) {
  try {
    // Pegar no máximo 200 caracteres para evitar erro de limite da API
    const cleanText = text.replace(/<[^>]+>/g, '').replace(/\[PAYWALL\]/g, '').trim().substring(0, 199);
    
    // Obter URL do áudio (Google Translate TTS endpoint)
    const url = googleTTS.getAudioUrl(cleanText, {
      lang: 'pt',
      slow: false,
      host: 'https://translate.google.com',
    });

    const response = await fetch(url);
    if (!response.ok) throw new Error(`Falha ao baixar TTS: ${response.statusText}`);
    const buffer = await response.arrayBuffer();
    fs.writeFileSync(outputPath, Buffer.from(buffer));
    return true;
  } catch (error) {
    console.error(`[VIDEO-MAKER] ❌ Erro no TTS:`, error.message);
    return false;
  }
}

/**
 * Renderiza um vídeo vertical a partir da imagem e áudio fornecidos
 */
function renderShort(postId, coverUrl, title, audioPath, subtitlePath, lofiPath, outPath) {
  return new Promise((resolve, reject) => {
    console.log(`[VIDEO-MAKER] 🎥 Renderizando Short para o post ${postId}...`);
    
    const command = ffmpeg()
      .input(coverUrl)
      .loop()
      .input(audioPath);

    // Prepara o caminho relativo da legenda para evitar erros do FFMPEG no Windows
    let subFilter = '';
    if (subtitlePath && fs.existsSync(subtitlePath)) {
      const relSubPath = path.relative(process.cwd(), subtitlePath).replace(/\\/g, '/');
      subFilter = `,subtitles=${relSubPath}:force_style='Fontname=Arial,Fontsize=18,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1'`;
    }

    let complexFilter = `[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.5)':d=1:s=1080x1920${subFilter}[v]`;

    const outputOptions = [
      '-map [v]',
      '-c:v libx264',
      '-tune stillimage',
      '-c:a aac',
      '-b:a 192k',
      '-pix_fmt yuv420p',
      '-shortest'
    ];

    if (lofiPath && fs.existsSync(lofiPath)) {
      command.input(lofiPath);
      // Áudio 1: TTS (volume original), Áudio 2: Lofi (volume 10%)
      complexFilter += `;[1:a]volume=1.0[a1];[2:a]volume=0.1[a2];[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[a]`;
      outputOptions.push('-map [a]');
    } else {
      outputOptions.push('-map 1:a');
    }

    command
      .complexFilter(complexFilter)
      .outputOptions(outputOptions)
      .save(outPath)
      .on('end', () => {
        console.log(`[VIDEO-MAKER] ✅ Short MP4 Gerado com Sucesso!`);
        resolve(outPath);
      })
      .on('error', (err) => {
        console.error(`[VIDEO-MAKER] 💥 Erro Fatal FFMPEG:`, err.message);
        reject(err);
      });
  });
}

/**
 * Processador da Fila (Cron Job Loop)
 */
async function processQueue() {
  const db = new Database(DB_PATH);
  
  console.log('[VIDEO-MAKER] 🕵️ Procurando roteiros de vídeo pendentes na fila...');
  
  // Usar JOIN se a tabela de post tiver coverImage, ou apenas buscar na fila
  // Note: swarm.ts grava id no post_id.
  const task = db.prepare(`
    SELECT v.*, p.coverImage 
    FROM video_render_queue v
    JOIN Post p ON p.id = v.post_id
    WHERE v.status = 'pending'
    ORDER BY v.created_at ASC
    LIMIT 1
  `).get();

  if (!task) {
    console.log('[VIDEO-MAKER] 💤 Nenhuma tarefa pendente. Descansando...');
    return;
  }

  console.log(`[VIDEO-MAKER] 🚀 Iniciando tarefa ID: ${task.id} | Post: ${task.title}`);

  // 1. Muda status para 'processing' para evitar duplicidade se rodar múltiplos crons
  db.prepare(`UPDATE video_render_queue SET status = 'processing', updated_at = CURRENT_TIMESTAMP WHERE id = ?`).run(task.id);

  try {
    const coverPath = path.resolve(process.cwd(), 'public' + task.coverImage.replace(/https?:\/\/[^\/]+/, ''));
    if (!fs.existsSync(coverPath)) {
      throw new Error(`Imagem de capa não encontrada localmente: ${coverPath}`);
    }

    // 2. Gerar Áudio (TTS) e Legendas
    console.log(`[VIDEO-MAKER] 🎙️ Sintetizando voz do locutor para: "${task.summary.substring(0, 30)}..."`);
    
    // Preparar pasta de podcasts (audios definitivos)
    const audioDir = path.resolve(process.cwd(), 'public/uploads/audios');
    if (!fs.existsSync(audioDir)) fs.mkdirSync(audioDir, { recursive: true });
    
    // Salvar como arquivo definitivo em vez de temp
    const audioPath = path.resolve(audioDir, `podcast_${task.post_id}.mp3`);
    const subtitlePath = path.resolve(process.cwd(), `public/uploads/temp_sub_${task.id}.srt`);
    const lofiPath = path.resolve(process.cwd(), `public/assets/lofi.mp3`);

    // Somente gerar se não existir (evita refazer se o FFMPEG falhou antes)
    let ttsSuccess = true;
    if (!fs.existsSync(audioPath)) {
      ttsSuccess = await generateTTS(task.summary, audioPath);
    }
    if (!ttsSuccess) throw new Error('Falha na geração do Áudio TTS.');

    // Gerar SRT Neural via Whisper (Agora Async)
    const srtSuccess = await generateSrt(task.summary, audioPath, subtitlePath);
    if (!srtSuccess) throw new Error('Falha na geração das legendas Whisper STT.');

    // 3. Renderizar FFMPEG
    const outFileName = `short_${task.post_id}_${Date.now()}.mp4`;
    const outPath = path.resolve(UPLOADS_DIR, outFileName);
    await renderShort(task.post_id, coverPath, task.title, audioPath, subtitlePath, lofiPath, outPath);

    // Limpeza de arquivo temporário
    // Nota: NÃO APAGAMOS MAIS O audioPath, POIS ELE É O EPISÓDIO DO PODCAST
    if (fs.existsSync(subtitlePath)) fs.unlinkSync(subtitlePath);

    // 3.5. Salvar o podcast no mediaPayload do Post
    try {
       const audioUrl = `/uploads/audios/podcast_${task.post_id}.mp3`;
       const payloadObj = {
          playlist: [{
             title: task.title,
             artist: "Apollo AI Podcast",
             url: audioUrl
          }]
       };
       // Promove o post para um Audio Track e salva o payload
       db.prepare(`UPDATE Post SET postType = 'audio_track', mediaPayload = ? WHERE id = ?`).run(JSON.stringify(payloadObj), task.post_id);
       console.log(`[VIDEO-MAKER] 🎧 Áudio MP3 preservado e Post promovido para 'audio_track' (Pronto para RSS Podcast!).`);
    } catch(e) {
       console.error(`[VIDEO-MAKER] Erro ao atualizar o payload de áudio do Post:`, e.message);
    }

    // 4. Atualizar DB
    // Opcional: Salvar a URL do vídeo no Post ou WebStory para ser exibido.
    let videoUrl = `/uploads/videos/${outFileName}`;
    
    // Suporte Híbrido S3 (Cloudflare R2 / AWS S3)
    if (process.env.S3_ACCESS_KEY && process.env.S3_SECRET_KEY && process.env.S3_BUCKET_NAME && process.env.S3_ENDPOINT) {
      console.log(`[VIDEO-MAKER] ☁️ Enviando MP4 para o Cloud Storage...`);
      const { S3Client, PutObjectCommand } = require('@aws-sdk/client-s3');
      const client = new S3Client({
        region: "auto",
        endpoint: process.env.S3_ENDPOINT,
        credentials: {
          accessKeyId: process.env.S3_ACCESS_KEY,
          secretAccessKey: process.env.S3_SECRET_KEY,
        },
      });
      const fileBuffer = fs.readFileSync(outPath);
      const command = new PutObjectCommand({
        Bucket: process.env.S3_BUCKET_NAME,
        Key: `videos/${outFileName}`,
        Body: fileBuffer,
        ContentType: 'video/mp4',
      });
      await client.send(command);
      
      // Apaga local
      fs.unlinkSync(outPath);
      
      const baseUrl = process.env.S3_PUBLIC_DOMAIN 
        ? process.env.S3_PUBLIC_DOMAIN.replace(/\/$/, "") 
        : process.env.S3_ENDPOINT.replace(/\/$/, "") + '/' + process.env.S3_BUCKET_NAME;
      
      videoUrl = `${baseUrl}/videos/${outFileName}`;
      console.log(`[VIDEO-MAKER] ☁️ MP4 Enviado para Nuvem: ${videoUrl}`);
    } else {
      console.log(`[VIDEO-MAKER] 🎉 Fila processada! Vídeo final salvo localmente em: ${videoUrl}`);
    }

    db.prepare(`UPDATE video_render_queue SET status = 'completed', updated_at = CURRENT_TIMESTAMP WHERE id = ?`).run(task.id);
    // Aqui você também pode fazer um UPDATE no Post para salvar a URL real.

  } catch (error) {
    console.error(`[VIDEO-MAKER] 🚨 Falha ao processar tarefa ${task.id}:`, error.message);
    db.prepare(`UPDATE video_render_queue SET status = 'failed', updated_at = CURRENT_TIMESTAMP WHERE id = ?`).run(task.id);
  }
}

// Inicia se rodado pelo terminal diretamente
if (require.main === module) {
  processQueue().then(() => {
    console.log('[VIDEO-MAKER] Execução avulsa finalizada.');
  });
}

module.exports = { processQueue };
