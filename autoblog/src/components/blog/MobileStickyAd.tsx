'use client';
import React, { useEffect, useState } from 'react';

export default function MobileStickyAd({ adHtml }: { adHtml?: string | null }) {
  const [isVisible, setIsVisible] = useState(false);
  const [isClosed, setIsClosed] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Aparece após rolar 300px
      if (window.scrollY > 300 && !isClosed) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isClosed]);

  if (!adHtml || isClosed) return null;

  return (
    <div 
      className={`fixed bottom-0 left-0 w-full z-[90] flex justify-center md:hidden transition-transform duration-500 ease-out ${isVisible ? 'translate-y-0' : 'translate-y-full'}`}
    >
      <div className="relative bg-theme-surface/90 backdrop-blur-xl border-t border-theme-border shadow-[0_-10px_40px_rgba(0,0,0,0.6)] flex items-center justify-center p-1 w-full min-h-[50px]">
        {/* Botão de Fechar */}
        <button 
          onClick={() => setIsClosed(true)}
          className="absolute -top-6 right-2 w-6 h-6 bg-theme-surface border border-theme-border text-theme-muted rounded-full flex items-center justify-center text-xs shadow-lg hover:text-white"
        >
          ✕
        </button>
        
        {/* Renderizador do Anúncio (Geralmente 320x50 ou 320x100) */}
        <div 
          className="w-full flex items-center justify-center overflow-hidden" 
          dangerouslySetInnerHTML={{ __html: adHtml }} 
        />
      </div>
    </div>
  );
}
