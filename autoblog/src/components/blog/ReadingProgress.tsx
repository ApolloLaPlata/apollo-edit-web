'use client';

import React, { useState, useEffect } from 'react';

export default function ReadingProgress({ title, readingTime }: { title?: string, readingTime?: number }) {
  const [progress, setProgress] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const updateProgress = () => {
      const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const scrollTop = document.documentElement.scrollTop;
      const percentage = (scrollTop / scrollHeight) * 100;
      setProgress(percentage);

      // Só exibe a barra se rolou além de 200px (header)
      if (scrollTop > 200) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', updateProgress);
    return () => window.removeEventListener('scroll', updateProgress);
  }, []);

  return (
    <>
      {/* 1. Barra Fina Superior Tradicional */}
      <div className="fixed top-0 left-0 w-full h-1 z-[70] bg-transparent pointer-events-none">
        <div 
          className="h-full bg-theme-accent shadow-[0_0_10px_rgba(var(--theme-accent-rgb),0.8)] transition-all duration-150 ease-out" 
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* 2. HUD Inteligente (Pill) flutuante */}
      {title && (
        <div className={`fixed top-4 left-1/2 -translate-x-1/2 z-[65] transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] ${isVisible ? 'translate-y-0 opacity-100 scale-100' : '-translate-y-16 opacity-0 scale-95'} pointer-events-none`}>
          <div className="glass-panel flex items-center gap-3 px-4 py-2 rounded-full border border-theme-border/50 shadow-2xl">
            {/* Mini gráfico circular de progresso */}
            <div className="relative w-6 h-6 flex items-center justify-center shrink-0">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" className="text-theme-border" strokeWidth="2" />
                <circle 
                  cx="12" cy="12" r="10" fill="none" stroke="currentColor" className="text-theme-accent" 
                  strokeWidth="2" strokeDasharray="62.83" strokeDashoffset={62.83 - (62.83 * progress) / 100}
                  strokeLinecap="round"
                />
              </svg>
            </div>
            
            <div className="hidden sm:block max-w-[200px] md:max-w-[400px] truncate text-xs font-bold text-theme-text">
              {title}
            </div>
            
            {readingTime && (
              <div className="text-[10px] uppercase tracking-widest font-bold text-theme-accent shrink-0 pl-3 border-l border-theme-border/50">
                {readingTime} min
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
