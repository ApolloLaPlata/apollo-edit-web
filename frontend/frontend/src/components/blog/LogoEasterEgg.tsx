'use client';
import React, { useState } from 'react';

export default function LogoEasterEgg({ children }: { children: React.ReactNode }) {
  const [clickCount, setClickCount] = useState(0);
  const [isSpinning, setIsSpinning] = useState(false);

  const handleClick = (e: React.MouseEvent) => {
    // Não impede a navegação natural (se for um Link), 
    // mas se for clicado muito rápido, acumula clicks.
    setClickCount(prev => {
      const newCount = prev + 1;
      if (newCount >= 5) {
        setIsSpinning(true);
        // Reseta o spin após a animação (3 segundos)
        setTimeout(() => {
          setIsSpinning(false);
          setClickCount(0);
        }, 3000);
        return 0; // reseta
      }
      return newCount;
    });

    // Zera o contador se demorar muito para clicar de novo
    setTimeout(() => {
      setClickCount(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
  };

  return (
    <div 
      onClick={handleClick}
      className={`inline-block transition-transform duration-1000 ${isSpinning ? 'animate-crazy-spin' : ''}`}
      title={clickCount > 2 ? "Continue clicando..." : undefined}
    >
      {children}
      
      {/* Confete invisível que só aparece no estado spinning */}
      {isSpinning && (
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none z-50">
          <div className="absolute w-2 h-2 bg-theme-accent rounded-full animate-ping" style={{ animationDuration: '0.5s' }}></div>
          <div className="absolute w-4 h-4 bg-white rounded-full animate-ping" style={{ animationDuration: '0.8s', animationDelay: '0.1s' }}></div>
          <div className="absolute w-8 h-8 border-2 border-theme-accent rounded-full animate-ping" style={{ animationDuration: '1s', animationDelay: '0.2s' }}></div>
        </div>
      )}
    </div>
  );
}
