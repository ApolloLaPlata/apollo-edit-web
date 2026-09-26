'use client';
import React, { useEffect, useRef, useState } from 'react';

interface ParallaxCoverProps {
  src: string;
  alt: string;
}

export default function ParallaxCover({ src, alt }: ParallaxCoverProps) {
  const [offset, setOffset] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Só ativa o parallax no desktop para evitar problemas de performance no mobile
    const isMobile = window.innerWidth < 768;
    if (isMobile) return;

    let rafId: number;

    const handleScroll = () => {
      if (!containerRef.current) return;
      
      const rect = containerRef.current.getBoundingClientRect();
      const windowHeight = window.innerHeight;

      // Só calcula o parallax se a imagem estiver visível na tela
      if (rect.top <= windowHeight && rect.bottom >= 0) {
        // Velocidade do parallax (0.3 = 30% da velocidade de rolagem)
        const scrollPosition = window.scrollY;
        // Centraliza o offset baseado no topo da página
        setOffset(scrollPosition * 0.3);
      }
    };

    const onScroll = () => {
      rafId = requestAnimationFrame(handleScroll);
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    
    // Init state
    handleScroll();

    return () => {
      window.removeEventListener('scroll', onScroll);
      cancelAnimationFrame(rafId);
    };
  }, []);

  return (
    <div 
      ref={containerRef} 
      className="w-full h-[300px] md:h-[450px] rounded-xl overflow-hidden relative shadow-2xl border border-theme-border group"
    >
      <img
        src={src}
        alt={alt}
        loading="eager"
        decoding="async"
        fetchPriority="high"
        className="w-full h-[130%] object-cover absolute top-[-15%] left-0 transition-transform duration-[50ms] ease-linear"
        style={{
          transform: `translate3d(0, ${offset}px, 0)`,
        }}
      />
      {/* Sombra interna para manter a legibilidade das bordas */}
      <div className="absolute inset-0 shadow-[inset_0_0_40px_rgba(0,0,0,0.5)] pointer-events-none rounded-xl"></div>
    </div>
  );
}
