'use client';
import React, { useState, useRef } from 'react';

export default function PodcastPlayer({ textToRead }: { textToRead: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handlePlayPodcast = async () => {
    setErrorMsg(null);
    if (audioRef.current && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    if (audioRef.current && !isPlaying) {
      audioRef.current.play();
      setIsPlaying(true);
      return;
    }

    // Gerar o audio via Gemini TTS
    setIsLoading(true);
    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToRead }),
      });
      const data = await response.json();

      if (data.success && data.audioBase64) {
        const audioSrc = `data:audio/ogg;base64,${data.audioBase64}`;
        const newAudio = new Audio(audioSrc);
        audioRef.current = newAudio;

        newAudio.onended = () => setIsPlaying(false);
        newAudio.play();
        setIsPlaying(true);
      } else {
        setErrorMsg('Falha ao gerar narração neural: ' + (data.error || 'Serviço temporariamente indisponível.'));
      }
    } catch (e) {
      setErrorMsg('Erro de rede ao conectar ao servidor de voz.');
    }
    setIsLoading(false);
  };

  return (
    <div className="mb-10 space-y-3">
      {errorMsg && (
        <div className="p-4 rounded-2xl bg-red-950/80 border border-red-500/40 text-red-300 text-xs font-semibold flex items-center justify-between shadow-lg">
          <div className="flex items-center gap-2">
            <span>⚠️</span>
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg(null)} className="text-slate-400 hover:text-white font-bold px-2">
            ✕
          </button>
        </div>
      )}

      <div className="p-8 bg-theme-surface/70 rounded-3xl border border-theme-border/60 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-2xl backdrop-blur-2xl relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-32 h-32 bg-theme-accent/5 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none group-hover:bg-theme-accent/10 transition-colors" />

        <div className="relative z-10 text-center sm:text-left">
          <h3 className="text-theme-text font-black text-2xl flex items-center justify-center sm:justify-start gap-3 mb-1">
            <span className="text-theme-accent text-3xl drop-shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.5)]">🎙️</span>
            Smart Podcast
          </h3>
          <p className="text-theme-muted text-sm font-medium">Escute a versão em áudio deste dossiê narrada por nossa redação.</p>
        </div>

        <button
          onClick={handlePlayPodcast}
          disabled={isLoading}
          className="relative z-10 bg-theme-accent hover:bg-theme-accent-hover disabled:opacity-50 text-white font-black py-4 px-8 rounded-2xl transition-all shadow-[0_0_20px_rgba(var(--theme-accent-rgb),0.4)] hover:shadow-[0_0_30px_rgba(var(--theme-accent-rgb),0.6)] flex items-center gap-3 whitespace-nowrap uppercase tracking-widest text-xs active:scale-95"
        >
          {isLoading ? (
            <>
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
              Sintetizando Áudio...
            </>
          ) : isPlaying ? (
            <>
              <svg className="w-6 h-6 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
                  clipRule="evenodd"
                ></path>
              </svg>
              Pausar Reprodução
            </>
          ) : (
            <>
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
                  clipRule="evenodd"
                ></path>
              </svg>
              Ouvir Dossiê
            </>
          )}
        </button>
      </div>
    </div>
  );
}
