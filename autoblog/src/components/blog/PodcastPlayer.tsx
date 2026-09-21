'use client';

import React, { useState, useEffect, useRef } from 'react';

/**
 * Player Neural de Artigos (Text-to-Speech)
 * Retém usuários que não gostam de ler, fazendo o navegador narrar o artigo com a voz nativa.
 * Incrementa absurdamente o "Tempo de Tela" (Dwell Time) e ajuda no ranqueamento do AdSense.
 */
export default function PodcastPlayer({ textToRead }: { textToRead: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [progress, setProgress] = useState(0);
  
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      setIsSupported(false);
      return;
    }

    // Removemos código markdown (###, **, *, links) antes de ler
    const cleanText = textToRead
      .replace(/[#*`_~]/g, '')
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Extrai texto do link
      .replace(/\n/g, ' ')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.05; // Levemente mais acelerado (Dinamismo)
    utterance.pitch = 1.0;

    // Tentativa de puxar a voz "Google português do Brasil" ou a nativa Premium do Mac/Windows
    const loadVoices = () => {
      const voices = window.speechSynthesis.getVoices();
      const ptBrVoice = voices.find(v => v.lang === 'pt-BR' && (v.name.includes('Google') || v.name.includes('Premium') || v.name.includes('Luciana')));
      if (ptBrVoice) utterance.voice = ptBrVoice;
    };

    window.speechSynthesis.onvoiceschanged = loadVoices;
    loadVoices();

    utterance.onboundary = (e) => {
      // Atualiza uma barra de progresso fake (estimativa) baseada nos caracteres lidos
      const percentage = Math.min((e.charIndex / cleanText.length) * 100, 100);
      setProgress(percentage);
    };

    utterance.onend = () => {
      setIsPlaying(false);
      setProgress(100);
    };

    utteranceRef.current = utterance;

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [textToRead]);

  const togglePlay = () => {
    if (!isSupported) return;

    if (isPlaying) {
      window.speechSynthesis.pause();
      setIsPlaying(false);
    } else {
      if (window.speechSynthesis.paused) {
         window.speechSynthesis.resume();
      } else {
         window.speechSynthesis.speak(utteranceRef.current!);
      }
      setIsPlaying(true);
    }
  };

  if (!isSupported) return null;

  return (
    <div className="flex items-center gap-4 bg-slate-900/80 backdrop-blur-md px-4 py-2 rounded-full border border-slate-700/60 shadow-lg shrink-0">
      <button 
        onClick={togglePlay}
        className="w-10 h-10 flex items-center justify-center bg-red-600 hover:bg-red-500 text-white rounded-full transition-all hover:scale-110 active:scale-95 shadow-md shadow-red-900/20"
        title="Escutar Reportagem"
      >
        {isPlaying ? (
          // Ícone de Pause
          <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg>
        ) : (
          // Ícone de Play
          <svg className="w-4 h-4 fill-current ml-1" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
        )}
      </button>

      <div className="flex flex-col w-32 md:w-48">
        <span className="text-[10px] uppercase font-bold tracking-widest text-slate-400">
          {isPlaying ? 'Lendo Agora...' : 'Ouvir Notícia'}
        </span>
        <div className="w-full bg-slate-800 h-1.5 mt-1.5 rounded-full overflow-hidden flex">
           <div 
             className="bg-red-500 h-full rounded-full transition-all duration-300 shadow-[0_0_8px_rgba(239,68,68,0.6)]" 
             style={{ width: `${progress}%` }}
           />
        </div>
      </div>
    </div>
  );
}
