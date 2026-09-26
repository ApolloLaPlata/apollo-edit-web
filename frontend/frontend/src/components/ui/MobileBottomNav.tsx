'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function MobileBottomNav({ lang, domain }: { lang: string; domain: string }) {
  const [isVisible, setIsVisible] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      // Esconder a barra quando rolar para baixo, mostrar quando rolar para cima
      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        setIsVisible(false);
      } else {
        setIsVisible(true);
      }
      
      setLastScrollY(currentScrollY);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [lastScrollY]);

  return (
    <div 
      className={`fixed bottom-0 left-0 w-full z-40 md:hidden transition-transform duration-300 ease-in-out ${
        isVisible ? 'translate-y-0' : 'translate-y-[120%]'
      }`}
    >
      {/* Background glassmorphism */}
      <div className="absolute inset-0 bg-theme-bg/85 backdrop-blur-xl border-t border-theme-border/50 shadow-[0_-4px_30px_rgba(0,0,0,0.1)]"></div>
      
      <div className="relative flex justify-around items-center px-2 py-3 pb-safe">
        {/* HOME */}
        <Link href={`/?lang=${lang}`} className="flex flex-col items-center gap-1 p-2 text-theme-text hover:text-theme-accent transition-colors group">
          <svg className="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span className="text-[10px] font-bold uppercase tracking-wider">Início</span>
        </Link>

        {/* BUSCAR */}
        <Link href={`/search?lang=${lang}`} className="flex flex-col items-center gap-1 p-2 text-theme-text hover:text-theme-accent transition-colors group">
          <svg className="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="text-[10px] font-bold uppercase tracking-wider">Busca</span>
        </Link>

        {/* STORIES (DESTAQUE) */}
        <Link href={`/stories?lang=${lang}`} className="flex flex-col items-center gap-1 p-2 -mt-4 relative group">
          <div className="bg-theme-accent text-white p-3 rounded-full shadow-lg shadow-theme-accent/50 group-hover:scale-110 group-hover:rotate-3 transition-transform ring-4 ring-theme-bg">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-theme-accent">Shorts</span>
        </Link>

        {/* FAVORITOS / SALVOS */}
        <Link href={`/profile?lang=${lang}`} className="flex flex-col items-center gap-1 p-2 text-theme-text hover:text-theme-accent transition-colors group">
          <svg className="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <span className="text-[10px] font-bold uppercase tracking-wider">Salvos</span>
        </Link>

        {/* CATEGORIAS */}
        <Link href={`/category?lang=${lang}`} className="flex flex-col items-center gap-1 p-2 text-theme-text hover:text-theme-accent transition-colors group">
          <svg className="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          <span className="text-[10px] font-bold uppercase tracking-wider">Menu</span>
        </Link>
      </div>
    </div>
  );
}
