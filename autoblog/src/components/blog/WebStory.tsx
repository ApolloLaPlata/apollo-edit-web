'use client';

import React, { useState, useEffect } from 'react';

/**
 * Motor de Web Stories (Google AMP UX)
 * Transforma uma notícia pesada em Slides rápidos de leitura vertical estilo Instagram/TikTok.
 */
export default function WebStory({ title, coverImage, paragraphs }: { title: string, coverImage: string, paragraphs: string[] }) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = paragraphs.length;

  useEffect(() => {
    // Auto-avança o Story a cada 10 segundos
    const timer = setInterval(() => {
      setCurrentSlide(prev => (prev < totalSlides - 1 ? prev + 1 : prev));
    }, 10000);
    return () => clearInterval(timer);
  }, [totalSlides]);

  const handleNext = () => {
    if (currentSlide < totalSlides - 1) setCurrentSlide(currentSlide + 1);
  };

  const handlePrev = () => {
    if (currentSlide > 0) setCurrentSlide(currentSlide - 1);
  };

  return (
    <div className="relative w-full h-[100dvh] md:h-[800px] md:max-w-md mx-auto bg-black overflow-hidden shadow-2xl md:rounded-3xl">
      
      {/* BACKGROUND IMAGE COM BLUR LENTO (Ken Burns Effect) */}
      <div 
        className="absolute inset-0 bg-cover bg-center transition-transform duration-[10000ms] ease-linear scale-105"
        style={{ 
          backgroundImage: `url(${coverImage})`,
          transform: currentSlide % 2 === 0 ? 'scale(1.15)' : 'scale(1.05)'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/40 to-black/95" />

      {/* BARRA DE PROGRESSO (STORIES) */}
      <div className="absolute top-4 left-4 right-4 flex gap-1 z-20">
        {paragraphs.map((_, i) => (
          <div key={i} className="h-1 flex-1 bg-white/30 rounded-full overflow-hidden">
            <div 
              className={`h-full bg-white transition-all duration-300 ${i === currentSlide ? 'w-full animate-[storyProgress_10s_linear]' : i < currentSlide ? 'w-full' : 'w-0'}`}
            />
          </div>
        ))}
      </div>

      {/* CONTEÚDO DO SLIDE ATUAL */}
      <div className="relative z-10 w-full h-full flex flex-col justify-end p-6 pb-24 text-white">
        <h1 className="text-3xl md:text-4xl font-black mb-6 leading-tight drop-shadow-lg text-transparent bg-clip-text bg-gradient-to-t from-slate-200 to-white">
          {title}
        </h1>
        
        <p className="text-lg md:text-xl font-medium leading-relaxed drop-shadow-md border-l-4 border-red-500 pl-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
          {paragraphs[currentSlide]}
        </p>
      </div>

      {/* ÁREAS DE CLIQUE INVISÍVEIS PARA NAVEGAR (Direita/Esquerda) */}
      <div className="absolute inset-y-0 left-0 w-1/3 z-20 cursor-pointer" onClick={handlePrev} />
      <div className="absolute inset-y-0 right-0 w-2/3 z-20 cursor-pointer" onClick={handleNext} />
      
      <div className="absolute bottom-6 left-0 w-full text-center z-20 pointer-events-none">
        <span className="text-white/50 text-xs uppercase tracking-widest font-bold">Deslize para ler</span>
      </div>
    </div>
  );
}
