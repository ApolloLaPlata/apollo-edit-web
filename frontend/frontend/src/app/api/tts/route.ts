import { NextResponse } from 'next/server';
import { generateModalXTTS, generateDualHostPodcast } from '@/lib/media/gemini-tts';

export async function POST(req: Request) {
  try {
    const { text, mode, title, niche } = await req.json();

    if (mode === 'dual_host') {
      const podcastData = await generateDualHostPodcast(title || 'Artigo do Portal', text || '', niche || 'Tecnologia & Inovação');
      return NextResponse.json({ success: true, podcast: podcastData });
    }

    if (!text) {
      return NextResponse.json({ error: 'Texto não fornecido' }, { status: 400 });
    }

    // O Motor de Voz Neural suporta leitura massiva (expandido de 500 para 4000 caracteres)
    const cleanText = text.substring(0, 4000).replace(/[#*`]/g, '');

    const base64Audio = await generateModalXTTS(cleanText);

    return NextResponse.json({ success: true, audioBase64: base64Audio });
  } catch (error: any) {
    console.error("Erro na rota de TTS:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
