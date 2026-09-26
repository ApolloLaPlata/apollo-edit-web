'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

export default function WebStoryPlayer({ initialStories, domain }: { initialStories: any[], domain: string }) {
  const [stories, setStories] = useState(initialStories);
  const [currentIndex, setCurrentIndex] = useState(0);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fallback caso não haja stories
  if (!stories || stories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-screen w-full bg-slate-950">
        <span className="text-6xl mb-6">📱</span>
        <h2 className="text-2xl font-black text-white uppercase tracking-widest mb-2">Sem Web Stories</h2>
        <p className="text-slate-400 mb-8 max-w-sm text-center text-sm">A redação ainda não preparou os conteúdos verticais dinâmicos de hoje.</p>
        <Link href="/" className="px-6 py-3 bg-theme-accent/20 border border-theme-accent/30 text-theme-accent rounded-xl hover:bg-theme-accent hover:text-white transition-all font-bold uppercase tracking-widest text-xs">
          Voltar ao Portal
        </Link>
      </div>
    );
  }

  // Interceptar o evento de scroll para atualizar o currentIndex (Doom Scrolling / Snap)
  const handleScroll = () => {
    if (containerRef.current) {
      const scrollY = containerRef.current.scrollTop;
      const height = window.innerHeight;
      const index = Math.round(scrollY / height);
      if (index !== currentIndex && index >= 0 && index < stories.length) {
        setCurrentIndex(index);
      }
    }
  };

  return (
    <div className="relative w-full h-[100dvh] bg-black overflow-hidden flex justify-center">
      
      {/* Botão Flutuante Superior (Sair) */}
      <Link href="/" className="absolute top-6 left-6 z-50 w-10 h-10 bg-black/40 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center hover:bg-black/80 transition-colors">
        <span className="text-white text-xl">✕</span>
      </Link>

      {/* Progress Bar (Visual Fake p/ Engajamento) */}
      <div className="absolute top-0 left-0 w-full h-1 bg-white/20 z-50">
         <div className="h-full bg-theme-accent transition-all duration-300" style={{ width: `${((currentIndex + 1) / stories.length) * 100}%` }} />
      </div>

      {/* Container de Rolagem (Snap) - Centralizado para visualização perfeita em Desktop ou Mobile */}
      <div 
        ref={containerRef}
        onScroll={handleScroll}
        className="w-full max-w-md h-[100dvh] overflow-y-scroll snap-y snap-mandatory hide-scrollbar relative bg-slate-900 border-x border-white/5"
      >
        {stories.map((story, index) => (
          <div key={story.id} className="w-full h-[100dvh] snap-start relative flex items-center justify-center overflow-hidden">
            
            {/* Media Background */}
            {story.imageUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={story.imageUrl} alt={story.title} className="absolute inset-0 w-full h-full object-cover" />
            ) : (
              <div className="absolute inset-0 bg-gradient-to-br from-slate-900 to-slate-800" />
            )}

            {/* Gradient Overlay for Text Readability */}
            <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent opacity-90 pointer-events-none" />

            {/* Interatividade / Botões Lado Direito */}
            <div className="absolute right-4 bottom-32 flex flex-col gap-6 z-40 items-center">
               <button className="w-12 h-12 bg-black/40 backdrop-blur-md rounded-full border border-white/20 flex flex-col items-center justify-center hover:bg-theme-accent/40 hover:border-theme-accent transition-all group">
                 <span className="text-xl group-hover:scale-125 transition-transform">❤️</span>
               </button>
               <span className="text-[10px] font-bold text-white shadow-black drop-shadow-md -mt-4">12k</span>
               
               <button className="w-12 h-12 bg-black/40 backdrop-blur-md rounded-full border border-white/20 flex flex-col items-center justify-center hover:bg-theme-accent/40 hover:border-theme-accent transition-all group">
                 <span className="text-xl group-hover:scale-125 transition-transform">💬</span>
               </button>
               <span className="text-[10px] font-bold text-white shadow-black drop-shadow-md -mt-4">500</span>

               <button className="w-12 h-12 bg-black/40 backdrop-blur-md rounded-full border border-white/20 flex flex-col items-center justify-center hover:bg-theme-accent/40 hover:border-theme-accent transition-all group">
                 <span className="text-xl group-hover:scale-125 transition-transform">🚀</span>
               </button>
               <span className="text-[10px] font-bold text-white shadow-black drop-shadow-md -mt-4">Share</span>
            </div>

            {/* Conteúdo Textual / Info na base */}
            <div className="absolute bottom-10 left-4 right-20 z-40">
               <div className="flex items-center gap-2 mb-3">
                  <div className="w-8 h-8 rounded-full bg-theme-accent flex items-center justify-center border-2 border-white">
                     <span className="text-black font-black text-xs uppercase">OE</span>
                  </div>
                  <span className="text-white font-bold text-sm tracking-wide shadow-black drop-shadow-md">Redação Especial</span>
                  <span className="px-2 py-0.5 bg-blue-600 rounded text-[9px] font-bold text-white uppercase tracking-widest ml-1">News</span>
               </div>
               
               <h2 className="text-2xl font-black text-white mb-2 leading-tight drop-shadow-lg shadow-black">
                 {story.title}
               </h2>
               
               <p className="text-slate-200 text-sm font-medium line-clamp-3 leading-relaxed drop-shadow-md shadow-black">
                 {story.content}
               </p>

               <div className="mt-4">
                  <button className="px-5 py-2.5 bg-white/20 backdrop-blur-md border border-white/30 rounded-xl text-white font-bold text-xs uppercase tracking-widest hover:bg-white hover:text-black transition-colors shadow-lg">
                    Saiba Mais ➔
                  </button>
               </div>
            </div>
          </div>
        ))}
      </div>
      
      <style dangerouslySetInnerHTML={{__html: `
        .hide-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .hide-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}} />
    </div>
  );
}
