'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function FloatingReadMore({ post, domain }: { post: any, domain: string }) {
  const [isVisible, setIsVisible] = useState(false);
  const [isClosed, setIsClosed] = useState(false);

  useEffect(() => {
    if (isClosed || !post) return;

    const handleScroll = () => {
      const scrolled = window.scrollY;
      const docHeight = document.documentElement.scrollHeight;
      const winHeight = window.innerHeight;
      
      const scrollPercent = (scrolled / (docHeight - winHeight)) * 100;
      
      // Surge sutilmente quando o leitor chega a 25% do artigo e some ao chegar no footer (95%)
      if (scrollPercent > 25 && scrollPercent < 95) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    // Chama uma vez para verificar estado inicial
    handleScroll();
    
    return () => window.removeEventListener('scroll', handleScroll);
  }, [isClosed, post]);

  if (!post || isClosed) return null;

  return (
    <div className={`fixed bottom-6 left-4 right-4 md:left-auto md:right-8 md:w-96 bg-theme-surface/90 backdrop-blur-2xl border border-theme-border rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-40 p-4 transition-all duration-700 ease-out transform ${isVisible ? 'translate-y-0 opacity-100 scale-100' : 'translate-y-32 opacity-0 scale-95 pointer-events-none'}`}>
      
      <button 
        onClick={() => setIsClosed(true)} 
        className="absolute -top-3 -right-3 w-7 h-7 bg-slate-800 text-white rounded-full flex items-center justify-center border border-slate-600 hover:bg-red-500 hover:border-red-600 transition-colors z-10 shadow-lg text-xs font-bold"
        aria-label="Fechar sugestão"
      >
        ✕
      </button>
      
      <Link href={`/blog/${post.slug}`} className="flex gap-4 group">
        {post.coverImage ? (
          <div className="w-24 h-20 rounded-xl overflow-hidden shrink-0 relative">
             <div className="absolute inset-0 bg-theme-accent/20 group-hover:bg-transparent transition-colors z-10"></div>
             {/* eslint-disable-next-line @next/next/no-img-element */}
             <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
          </div>
        ) : (
          <div className="w-24 h-20 rounded-xl bg-slate-800 shrink-0 flex items-center justify-center text-slate-600">
             <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path></svg>
          </div>
        )}
        <div className="flex flex-col justify-center flex-1">
          <span className="text-[10px] font-black text-theme-accent uppercase tracking-widest mb-1 flex items-center gap-1">
             <span className="w-1.5 h-1.5 rounded-full bg-theme-accent animate-pulse"></span>
             Leia Também
          </span>
          <h4 className="text-sm font-bold text-slate-200 leading-snug line-clamp-2 group-hover:text-white transition-colors">
            {post.title}
          </h4>
        </div>
      </Link>
    </div>
  );
}
