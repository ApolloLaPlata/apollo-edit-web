'use client';
import { useState, useEffect, useRef } from 'react';

export default function TextToSpeechPlayer({ audioUrl }: { audioUrl?: string | null }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [readingTime, setReadingTime] = useState(0);
  const [isSupported, setIsSupported] = useState(false);
  
  const synthRef = useRef<SpeechSynthesis | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  
  useEffect(() => {
    // Se tivermos audioUrl real (Do Apollo), usamos HTML Audio Element
    if (audioUrl) {
      setIsSupported(true);
      audioRef.current = new Audio(audioUrl);
      
      audioRef.current.onended = () => {
        setIsPlaying(false);
        setIsPaused(false);
      };
      
      // Quando carregado, pode-se ler a duração (opcional)
      audioRef.current.onloadedmetadata = () => {
        setReadingTime(Math.max(1, Math.ceil(audioRef.current!.duration / 60)));
      };
      
      return () => {
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.src = '';
        }
      };
    }

    // Fallback: Web Speech API
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
      setIsSupported(true);
      
      // Estimar tempo de leitura visual
      const article = document.querySelector('.zen-article');
      if (article) {
        const text = article.textContent || '';
        const words = text.split(/\s+/).length;
        setReadingTime(Math.max(1, Math.ceil(words / 150))); // aprox 150 words por min
      }
    }
    
    return () => {
      if (synthRef.current) {
        synthRef.current.cancel();
      }
    };
  }, [audioUrl]);

  const handlePlay = () => {
    // -----------------------------------------------------
    // Fluxo com Áudio Real (Apollo)
    // -----------------------------------------------------
    if (audioUrl && audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPaused(true);
        setIsPlaying(false);
      } else {
        audioRef.current.play().catch(e => console.error("Erro ao reproduzir áudio:", e));
        setIsPaused(false);
        setIsPlaying(true);
      }
      return;
    }

    // -----------------------------------------------------
    // Fluxo Fallback (SpeechSynthesis)
    // -----------------------------------------------------
    if (!synthRef.current) return;
    
    if (isPaused) {
      synthRef.current.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    if (isPlaying) {
      synthRef.current.pause();
      setIsPaused(true);
      setIsPlaying(false);
      return;
    }

    synthRef.current.cancel();

    const article = document.querySelector('.zen-article');
    if (!article) return;
    
    const textToRead = (article as HTMLElement).innerText || article.textContent || '';
    if (!textToRead.trim()) return;

    const utterance = new SpeechSynthesisUtterance(textToRead);
    utterance.lang = 'pt-BR'; 
    utterance.rate = 1.05; 
    utterance.pitch = 1.0;
    
    const voices = synthRef.current.getVoices();
    const brVoice = voices.find(v => v.lang.includes('pt-BR') && (v.name.includes('Google') || v.name.includes('Microsoft')));
    if (brVoice) utterance.voice = brVoice;
    
    utterance.onend = () => { setIsPlaying(false); setIsPaused(false); };
    utterance.onerror = () => { setIsPlaying(false); setIsPaused(false); };

    synthRef.current.speak(utterance);
    setIsPlaying(true);
    setIsPaused(false);
  };
  
  const handleStop = () => {
    if (audioUrl && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    } else if (synthRef.current) {
      synthRef.current.cancel();
    }
    setIsPlaying(false);
    setIsPaused(false);
  };

  if (!isSupported) return null;

  return (
    <div className="flex flex-col sm:flex-row items-center gap-5 bg-gradient-to-r from-theme-surface to-slate-900 border border-theme-border/60 rounded-[20px] p-5 shadow-2xl max-w-2xl my-10 relative overflow-hidden group">
      
      {/* Efeito Glow Interno */}
      <div className={"absolute top-0 right-0 w-32 h-32 bg-theme-accent/5 rounded-full blur-2xl pointer-events-none transition-opacity duration-1000 " + (isPlaying ? 'opacity-100' : 'opacity-0')}></div>
      
      {/* Botão Principal Play/Pause */}
      <button 
        onClick={handlePlay}
        className="w-16 h-16 rounded-full shrink-0 flex items-center justify-center bg-theme-accent text-white shadow-[0_0_20px_rgba(var(--theme-accent-rgb),0.4)] hover:scale-105 hover:bg-theme-accent-hover transition-all relative z-10"
        aria-label={isPlaying ? 'Pausar leitura' : 'Ouvir artigo'}
      >
        {isPlaying ? (
           <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M11 22h-4v-20h4v20zm6-20h-4v20h4v-20z"/></svg>
        ) : (
           <svg className="w-7 h-7 ml-1" fill="currentColor" viewBox="0 0 24 24"><path d="M3 22v-20l18 10-18 10z"/></svg>
        )}
      </button>

      {/* Informações da Faixa */}
      <div className="flex flex-col flex-1 w-full text-center sm:text-left relative z-10">
        <h4 className="text-sm font-black text-white uppercase tracking-widest flex items-center justify-center sm:justify-start gap-3">
          {audioUrl ? 'Narração Oficial' : 'Ouça este artigo'}
          
          {/* Waveform Animation */}
          {(isPlaying || isPaused) && (
            <span className="flex items-center gap-1 h-4">
              <span className={"w-1 bg-theme-accent rounded-full transition-all duration-200 " + (isPlaying ? 'h-full animate-[ping_1s_infinite]' : 'h-1 opacity-50')} style={{ animationDelay: '0s' }}></span>
              <span className={"w-1 bg-theme-accent rounded-full transition-all duration-200 " + (isPlaying ? 'h-2/3 animate-[ping_1.2s_infinite]' : 'h-1 opacity-50')} style={{ animationDelay: '0.2s' }}></span>
              <span className={"w-1 bg-theme-accent rounded-full transition-all duration-200 " + (isPlaying ? 'h-full animate-[ping_0.8s_infinite]' : 'h-1 opacity-50')} style={{ animationDelay: '0.4s' }}></span>
            </span>
          )}
        </h4>
        <p className="text-xs text-theme-muted mt-2 font-medium">
          {isPlaying 
            ? (audioUrl ? 'Reproduzindo áudio...' : 'Narração IA ativa...') 
            : isPaused 
              ? 'Leitura pausada pelo usuário.' 
              : "Aproximadamente " + readingTime + " min de áudio nativo."}
        </p>
      </div>
      
      {/* Botão de Parada Total */}
      {(isPlaying || isPaused) && (
        <button 
          onClick={handleStop}
          className="text-[10px] font-bold text-slate-400 hover:text-white uppercase tracking-widest transition-all px-4 py-2 bg-slate-800/50 hover:bg-red-500 rounded-lg relative z-10"
        >
          Parar
        </button>
      )}
    </div>
  );
}
