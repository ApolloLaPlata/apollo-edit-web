const fs = require('fs');
const { execSync } = require('child_process');
const ffprobeStatic = require('ffprobe-static');
const OpenAI = require('openai');

require('dotenv').config();

function getAudioDuration(audioPath) {
  try {
    const output = execSync(`"${ffprobeStatic.path}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${audioPath}"`);
    return parseFloat(output.toString().trim());
  } catch (err) {
    console.error('[SUBTITLE] Erro ao obter duração do áudio:', err.message);
    return 10; // Fallback
  }
}

function formatTime(seconds) {
  const date = new Date(seconds * 1000);
  const hh = String(date.getUTCHours()).padStart(2, '0');
  const mm = String(date.getUTCMinutes()).padStart(2, '0');
  const ss = String(date.getUTCSeconds()).padStart(2, '0');
  const ms = String(date.getUTCMilliseconds()).padStart(3, '0');
  return `${hh}:${mm}:${ss},${ms}`;
}

// O gerador antigo será usado como fallback caso falte chave da OpenAI ou ocorra falha de rede
function generateSrtFallback(text, audioPath, outputPath) {
  console.log('[SUBTITLE] 📝 Gerando legendas matemáticas (Fallback)...');
  
  const cleanText = text.replace(/<[^>]+>/g, '').replace(/\[PAYWALL\]/g, '').trim().substring(0, 199);
  const words = cleanText.split(/\s+/).filter(w => w.length > 0);
  
  if (words.length === 0) return false;

  const totalDuration = getAudioDuration(audioPath);
  const timePerWord = totalDuration / words.length;

  let srtContent = '';
  let index = 1;
  let currentTime = 0;
  
  const wordsPerChunk = 4;
  for (let i = 0; i < words.length; i += wordsPerChunk) {
    const chunk = words.slice(i, i + wordsPerChunk).join(' ');
    const chunkDuration = words.slice(i, i + wordsPerChunk).length * timePerWord;
    
    const startTime = formatTime(currentTime);
    const endTime = formatTime(currentTime + chunkDuration);
    
    srtContent += `${index}\n`;
    srtContent += `${startTime} --> ${endTime}\n`;
    srtContent += `${chunk}\n\n`;
    
    currentTime += chunkDuration;
    index++;
  }

  fs.writeFileSync(outputPath, srtContent);
  return true;
}

/**
 * Motor Principal: Whisper STT (OpenAI)
 * Extrai o SRT hiper-preciso
 */
async function generateSrt(text, audioPath, outputPath) {
  console.log('[SUBTITLE] 🎙️ Iniciando Transcrição Neural Whisper-1...');
  
  if (!process.env.OPENAI_API_KEY) {
     console.log('[SUBTITLE] ⚠️ OPENAI_API_KEY não encontrada no ambiente. Utilizando Fallback matemático.');
     return generateSrtFallback(text, audioPath, outputPath);
  }

  try {
     const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });
     
     // O Whisper suporta o formato SRT nativamente na resposta!
     const transcription = await openai.audio.transcriptions.create({
       file: fs.createReadStream(audioPath),
       model: 'whisper-1',
       response_format: 'srt'
     });

     fs.writeFileSync(outputPath, transcription);
     
     // Demonstração da riqueza do arquivo gerado
     const preview = transcription.substring(0, 150).replace(/\n/g, '\\n');
     console.log(`[SUBTITLE] ✅ SRT gerado via Whisper com perfeição! Preview: ${preview}...`);
     return true;

  } catch (error) {
     console.error('[SUBTITLE] ❌ Erro na API do Whisper:', error.message);
     console.log('[SUBTITLE] 🔄 Acionando motor matemático (Fallback)...');
     return generateSrtFallback(text, audioPath, outputPath);
  }
}

module.exports = { generateSrt };
