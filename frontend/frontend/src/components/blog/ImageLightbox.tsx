'use client';
import React, { useEffect, useState, useRef } from 'react';

export default function ImageLightbox({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [imgSrc, setImgSrc] = useState('');
  const [imgAlt, setImgAlt] = useState('');
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleImageClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'IMG') {
        const img = target as HTMLImageElement;
        // Ignorar icones pequenos ou imagens que não pertencem ao artigo
        if (img.width < 100) return;
        
        setImgSrc(img.src);
        setImgAlt(img.alt || 'Imagem do Artigo');
        setIsOpen(true);
      }
    };

    const container = containerRef.current;
    if (container) {
      // Adiciona o cursor de zoom in nas imagens via CSS
      const imgs = container.querySelectorAll('img');
      imgs.forEach(img => {
        if (img.width >= 100) {
          img.style.cursor = 'zoom-in';
          img.style.transition = 'transform 0.3s ease';
        }
      });
      container.addEventListener('click', handleImageClick);
    }

    return () => {
      if (container) {
        container.removeEventListener('click', handleImageClick);
      }
    };
  }, [children]); // Re-run if children change

  // Bloqueia o scroll do body quando o lightbox está aberto
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Fechar com a tecla ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setIsOpen(false);
    };
    if (isOpen) window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  return (
    <>
      <div ref={containerRef} className="lightbox-container">
        {children}
      </div>

      {isOpen && (
        <div 
          className="fixed inset-0 z-[999999] bg-slate-950/95 backdrop-blur-2xl flex flex-col items-center justify-center cursor-zoom-out transition-opacity duration-300 animate-in fade-in"
          onClick={() => setIsOpen(false)}
        >
          {/* Botão Fechar no Topo */}
          <div className="absolute top-6 right-6 w-12 h-12 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center backdrop-blur-md transition-colors cursor-pointer text-white">
             <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
             </svg>
          </div>

          <img 
            src={imgSrc} 
            alt={imgAlt}
            className="max-w-[95vw] max-h-[85vh] object-contain rounded-xl shadow-[0_0_50px_rgba(0,0,0,0.5)] animate-in zoom-in-95 duration-300"
            onClick={(e) => e.stopPropagation()} // Impede que clicar na foto feche
          />
          
          {imgAlt && (
            <div className="absolute bottom-10 px-6 py-3 bg-black/60 backdrop-blur-md text-white/80 text-sm font-medium rounded-full max-w-[80vw] text-center">
              {imgAlt}
            </div>
          )}
        </div>
      )}
    </>
  );
}
