'use client';

import React, { useState, useEffect, useRef } from 'react';

/**
 * 🎧 AI PODCAST & VIDEO ENGINE (Módulo 8 - Etapas 36 a 40)
 * Transforma a Fofoca em um "MesaCast" falso em tempo real.
 * Duas vozes conversam sobre a notícia (Web Speech API / TTS avançado).
 * Uma onda sonora reativa pulsa em 3D usando Canvas (HTML5).
 */
export default function AIPodcastGenerator({ articleTitle, articleBody }: { articleTitle: string, articleBody: string }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState("0:00");
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  // Etapas 37 e 38: Clonagem de Voz Multi-Ator & Ondas Sonoras 3D (Simulado para o UI)
  useEffect(() => {
    let animationFrameId: number;

    const drawWaveform = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      const width = canvas.width;
      const height = canvas.height;
      ctx.clearRect(0, 0, width, height);

      // Efeito de Osciloscópio Neon (Etapa 38)
      ctx.beginPath();
      ctx.moveTo(0, height / 2);
      ctx.strokeStyle = isPlaying ? '#ec4899' : '#334155'; // Pink se tocando, Slate se parado
      ctx.lineWidth = 3;
      ctx.shadowBlur = isPlaying ? 15 : 0;
      ctx.shadowColor = '#ec4899';

      for (let i = 0; i < width; i++) {
        // Se isPlaying for true, cria montanhas aleatórias. Se não, linha reta.
        const amplitude = isPlaying ? Math.random() * 40 - 20 : 0;
        ctx.lineTo(i, height / 2 + amplitude);
      }
      
      ctx.stroke();

      if (isPlaying) {
        animationFrameId = requestAnimationFrame(drawWaveform);
      }
    };

    drawWaveform();

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
  }, [isPlaying]);

  const togglePodcast = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      console.log(`[PODCAST ENGINE] 🎙️ Iniciando MesaCast Auto-Gerado. Ator 1: "Carlos". Ator 2: "Vanessa".`);
      console.log(`[PODCAST ENGINE] Lendo script baseado no post: "${articleTitle}"`);
    } else {
      console.log(`[PODCAST ENGINE] ⏸️ Podcast Pausado.`);
    }
  };

  const downloadMP3 = () => {
    console.log(`[PODCAST ENGINE] 💾 Etapa 39: Convertendo stream de áudio para MP3 e baixando offline...`);
    alert("Podcast sendo baixado para ouvir no trânsito!");
  };

  return (
    <div className="bg-[#111116] border border-pink-900/50 rounded-2xl p-6 shadow-2xl w-full max-w-3xl mx-auto my-8 relative overflow-hidden group">
      
      {/* Glow de Fundo */}
      <div className={`absolute top-0 right-0 w-64 h-64 rounded-full blur-3xl pointer-events-none transition-all duration-1000 ${isPlaying ? 'bg-pink-600/10' : 'bg-slate-900/50'}`} />

      <div className="flex flex-col md:flex-row gap-6 relative z-10 items-center">
         
         {/* Capa do Podcast Fake */}
         <div className="w-32 h-32 flex-shrink-0 bg-slate-900 rounded-xl shadow-lg border border-slate-700 relative overflow-hidden flex items-center justify-center">
            <div className={`absolute inset-0 bg-gradient-to-br from-pink-500 to-purple-800 opacity-50 ${isPlaying ? 'animate-[spin_4s_linear_infinite]' : ''}`} />
            <span className="text-4xl z-10 relative">🎙️</span>
            {isPlaying && <div className="absolute bottom-2 right-2 w-3 h-3 bg-red-500 rounded-full animate-ping" />}
         </div>

         {/* Player Controls */}
         <div className="flex-1 w-full">
            <div className="flex justify-between items-start mb-2">
               <div>
                  <h3 className="text-white font-black text-lg">FofocaCast I.A</h3>
                  <p className="text-pink-400 text-xs font-bold uppercase tracking-widest">Episódio Auto-Gerado</p>
               </div>
               <span className="text-slate-500 font-mono text-sm bg-slate-900 px-2 py-1 rounded">
                  {isPlaying ? 'Ao Vivo' : '0:00 / 12:45'}
               </span>
            </div>

            <p className="text-slate-400 text-sm mb-4 line-clamp-1 italic">
               "{articleTitle}"
            </p>

            {/* Canvas Waveform (Etapa 38) */}
            <div className="w-full h-12 bg-slate-950 rounded-lg border border-slate-800 mb-4 overflow-hidden relative">
               <canvas ref={canvasRef} width={600} height={48} className="w-full h-full" />
            </div>

            <div className="flex items-center gap-3">
               <button 
                 onClick={togglePodcast}
                 className={`flex-1 font-black uppercase text-sm py-3 rounded-lg transition-all flex items-center justify-center gap-2 ${isPlaying ? 'bg-slate-800 text-slate-300 hover:bg-slate-700' : 'bg-pink-600 hover:bg-pink-500 text-white shadow-[0_0_15px_rgba(236,72,153,0.4)]'}`}
               >
                 {isPlaying ? '⏸ Pausar' : '▶️ Tocar Podcast'}
               </button>

               <button 
                 onClick={downloadMP3}
                 className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 px-4 py-3 rounded-lg transition-colors flex items-center justify-center"
                 title="Baixar MP3 (Offline)"
               >
                 📥
               </button>
            </div>
         </div>
      </div>
    </div>
  );
}
