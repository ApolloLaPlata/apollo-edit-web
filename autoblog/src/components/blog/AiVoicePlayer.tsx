'use client';

import React, { useState, useEffect } from 'react';

/**
 * 🎙️ RÁDIO I.A (Text-To-Speech)
 * Retenção extrema: Lê a fofoca para o usuário enquanto ele lava louça ou dirige.
 */
export default function AiVoicePlayer({ textToRead, title }: { textToRead: string, title: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [synth, setSynth] = useState<SpeechSynthesis | null>(null);
  const [voice, setVoice] = useState<SpeechSynthesisVoice | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const s = window.speechSynthesis;
      setSynth(s);

      // Carrega a melhor voz do SO (Focando em Português-BR feminino pra fofoca)
      const loadVoices = () => {
        const voices = s.getVoices();
        const ptVoice = voices.find(v => v.lang === 'pt-BR' && v.name.includes('Google')) || 
                        voices.find(v => v.lang === 'pt-BR') || 
                        voices[0];
        setVoice(ptVoice || null);
      };

      loadVoices();
      if (speechSynthesis.onvoiceschanged !== undefined) {
        speechSynthesis.onvoiceschanged = loadVoices;
      }
    }
    
    return () => {
       if (synth) synth.cancel(); // Para de falar ao fechar a aba
    };
  }, []);

  const handlePlay = () => {
    if (!synth) return alert("Seu navegador não suporta a Rádio I.A.");

    if (isPaused) {
      synth.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    if (isPlaying) {
      synth.pause();
      setIsPaused(true);
      setIsPlaying(false);
      return;
    }

    // Prepara a leitura Dramática
    const utterance = new SpeechSynthesisUtterance(`Rádio Auto Blog. Notícia exclusiva: ${title}. ${textToRead}`);
    if (voice) utterance.voice = voice;
    utterance.rate = 1.05; // Levemente mais rápido
    utterance.pitch = 1.2; // Mais estridente para dar tom de "urgência/fofoca"

    utterance.onend = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    synth.speak(utterance);
    setIsPlaying(true);
  };

  return (
    <div className="bg-gradient-to-r from-red-950 to-slate-900 border border-red-900/50 rounded-2xl p-6 flex items-center justify-between shadow-2xl mb-10 w-full animate-in zoom-in duration-500 hover:border-red-500/50 transition-colors group">
      <div className="flex items-center gap-6">
        <button 
          onClick={handlePlay}
          className="w-16 h-16 bg-red-600 hover:bg-red-500 text-white rounded-full flex items-center justify-center shadow-[0_0_20px_rgba(220,38,38,0.4)] hover:scale-105 transition-all focus:outline-none"
        >
          {isPlaying ? (
            <svg className="w-8 h-8 fill-current" viewBox="0 0 24 24"><path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/></svg> // Pause
          ) : (
            <svg className="w-8 h-8 fill-current ml-2" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg> // Play
          )}
        </button>
        <div>
          <h3 className="text-white font-black text-lg uppercase tracking-widest flex items-center gap-2">
            Rádio I.A <span className="relative flex h-3 w-3"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span></span>
          </h3>
          <p className="text-red-300/80 text-sm font-medium mt-1 group-hover:text-red-200 transition-colors">
            {isPlaying ? "📻 Transmitindo a fofoca ao vivo..." : "Escute essa matéria no fone (Hands-Free)"}
          </p>
        </div>
      </div>
      
      {isPlaying && (
         <div className="hidden md:flex gap-1 h-8 items-end opacity-80">
            <div className="w-2 bg-red-500 rounded-t-sm h-full animate-[bounce_1s_infinite_ease-in-out_alternate]"></div>
            <div className="w-2 bg-red-400 rounded-t-sm h-3/4 animate-[bounce_0.8s_infinite_ease-in-out_alternate]"></div>
            <div className="w-2 bg-amber-500 rounded-t-sm h-1/2 animate-[bounce_1.2s_infinite_ease-in-out_alternate]"></div>
            <div className="w-2 bg-red-600 rounded-t-sm h-full animate-[bounce_0.9s_infinite_ease-in-out_alternate]"></div>
         </div>
      )}
    </div>
  );
}
