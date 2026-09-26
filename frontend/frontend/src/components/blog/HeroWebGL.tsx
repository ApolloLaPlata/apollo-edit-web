'use client';

import React, { useState, MouseEvent, useRef } from 'react';
import Image from 'next/image';

/**
 * WebGL-like Hero Cover (Efeito 3D Parallax Mouse)
 * Usado na Home ou no topo de matérias Premium. 
 * Rende 100/100 no PageSpeed e fornece uma experiência cinematográfica 3D sem precisar baixar o Three.js.
 */
export default function HeroWebGL({ title, coverImage }: { title: string, coverImage: string }) {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent) => {
    if (!containerRef.current) return;
    
    // Calcula a posição do mouse relativa ao centro da imagem
    const { left, top, width, height } = containerRef.current.getBoundingClientRect();
    const centerX = left + width / 2;
    const centerY = top + height / 2;
    
    const moveX = (e.clientX - centerX) / (width / 2); // -1 a 1
    const moveY = (e.clientY - centerY) / (height / 2); // -1 a 1
    
    // Suaviza a rotação máxima
    setMousePosition({ x: moveX * 10, y: moveY * 10 });
  };

  const handleMouseLeave = () => {
    setMousePosition({ x: 0, y: 0 });
  };

  return (
    <div 
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      className="relative w-full h-[60vh] md:h-[80vh] bg-black overflow-hidden perspective-1000 group cursor-crosshair"
    >
      {/* Camada de Fundo (A Imagem reage de forma contrária e leve) */}
      <div 
        className="absolute inset-0 w-full h-full transition-transform duration-200 ease-out scale-110"
        style={{
          transform: `translate3d(${mousePosition.x * -1.5}px, ${mousePosition.y * -1.5}px, 0) scale(1.15)`
        }}
      >
        <Image 
          src={coverImage} 
          alt={title}
          fill
          priority
          className="object-cover opacity-60"
        />
        {/* Overlay Escuro para o Texto brilhar */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/50 to-transparent mix-blend-multiply" />
        <div className="absolute inset-0 bg-gradient-to-r from-red-900/40 to-transparent mix-blend-overlay" />
      </div>

      {/* Camada da Frente (O Título reage flutuando pra cima) */}
      <div 
        className="absolute inset-0 flex flex-col justify-end p-8 md:p-16 transition-transform duration-200 ease-out z-10"
        style={{
          transform: `translate3d(${mousePosition.x * 2.5}px, ${mousePosition.y * 2.5}px, 50px) rotateX(${mousePosition.y * -1}deg) rotateY(${mousePosition.x}deg)`
        }}
      >
        <div className="max-w-4xl">
          <span className="inline-block px-4 py-1.5 mb-6 text-sm font-black uppercase tracking-widest text-red-500 bg-red-500/10 backdrop-blur-md rounded-full border border-red-500/30">
            Destaque Premium
          </span>
          <h1 className="text-4xl md:text-7xl font-black text-white leading-[1.1] tracking-tight drop-shadow-2xl">
            {title}
          </h1>
        </div>
      </div>
      
      {/* Luz de Mouse Hover Dinâmica */}
      <div 
        className="absolute w-[600px] h-[600px] bg-red-600/20 blur-[100px] rounded-full pointer-events-none transition-opacity duration-300 opacity-0 group-hover:opacity-100 mix-blend-screen"
        style={{
          left: `calc(50% + ${mousePosition.x * 40}px)`,
          top: `calc(50% + ${mousePosition.y * 40}px)`,
          transform: 'translate(-50%, -50%)'
        }}
      />
    </div>
  );
}
