'use client';

import React, { useEffect, useState, useRef } from 'react';
// Importação simulada do framer-motion (já que não instalaremos o pacote de fato aqui no bash)
// import { motion, useScroll, useTransform } from 'framer-motion';

/**
 * 🌌 WRAPPER CINEMÁTICO V6 (Framer Motion + WebGL Shader Emulado)
 * Etapas 11 a 15 consolidadas.
 * Transforma o Blog em uma experiência de imersão profunda (Liquid UX).
 */
export default function CinematicWrapper({ children, dangerLevel = 50 }: { children: React.ReactNode, dangerLevel?: number }) {
  const [scrollY, setScrollY] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1. Simula Scroll-Jacking Imersivo (Etapa 15)
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // 2. Cálculo do Shader de Fundo baseado no Danger Level (Fofoca Quente)
  // Se a fofoca for nível 100, o fundo pulsa vermelho sague. Se for leve, azul ciano.
  const isHighDanger = dangerLevel > 70;
  
  return (
    <div ref={containerRef} className="relative min-h-screen overflow-hidden bg-black text-white perspective-1000">
      
      {/* =========================================================
          ETAPA 13: SHADERS WEBGL (Emulado com CSS Dinâmico GPU-Acelerado)
          O background reage ao SCROLL (efeito Parallax Distorcido).
      ========================================================= */}
      <div 
        className="fixed inset-0 pointer-events-none -z-20 transition-transform duration-1000 ease-out"
        style={{
          transform: `translateY(${scrollY * 0.15}px) scale(${1 + scrollY * 0.0005})`,
          opacity: 0.4
        }}
      >
         <div className={`absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,_var(--tw-gradient-stops))] ${isHighDanger ? 'from-red-900 via-black to-black' : 'from-blue-900 via-black to-black'}`} />
         
         {/* Malha de Holograma Líquido */}
         <div className="absolute inset-0 opacity-20 mix-blend-overlay bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] animate-[pulse_4s_infinite_alternate]" />
      </div>

      {/* =========================================================
          ETAPA 14: TEXTOS 3D DINÂMICOS (Tremor Leve / Glitch)
      ========================================================= */}
      <div className="fixed top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-red-500 to-transparent opacity-50 z-50 animate-[scan_3s_ease-in-out_infinite]" />

      {/* =========================================================
          ETAPA 11 e 12: FRAMER MOTION (Transições Líquidas)
          Como não instalamos o pacote no bash, usamos CSS Animation puras emulando 'AnimatePresence'.
      ========================================================= */}
      <main 
        className="relative z-10 w-full h-full max-w-7xl mx-auto px-6 py-12 animate-in fade-in slide-in-from-bottom-12 duration-[1200ms] ease-[cubic-bezier(0.16,1,0.3,1)]"
        style={{
          // Efeito de Tilt 3D com o Scroll (Scroll-Jacking)
          transform: `rotateX(${Math.min(scrollY * 0.01, 10)}deg)`,
          transformOrigin: 'top center'
        }}
      >
         {children}
      </main>

    </div>
  );
}
