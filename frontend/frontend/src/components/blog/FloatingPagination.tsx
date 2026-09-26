'use client';
import React from 'react';
import Link from 'next/link';

export default function FloatingPagination({ 
  currentPage, 
  hasNextPage, 
  lang 
}: { 
  currentPage: number; 
  hasNextPage: boolean; 
  lang: string;
}) {
  if (currentPage === 1 && !hasNextPage) return null;

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-[60] flex items-center gap-2 bg-slate-900/90 backdrop-blur-xl p-2 rounded-full border border-slate-700/50 shadow-[0_10px_40px_rgba(0,0,0,0.8)] transition-all hover:scale-105 group hover:border-theme-accent/50">
      
      {currentPage > 1 ? (
        <Link 
          href={`/?lang=${lang}&page=${currentPage - 1}`}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-800 hover:bg-theme-accent text-slate-300 hover:text-white transition-colors shadow-inner"
          aria-label="Página Anterior"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7"></path></svg>
        </Link>
      ) : (
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-800/30 text-slate-700 cursor-not-allowed">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7"></path></svg>
        </div>
      )}

      <div className="px-4 text-[10px] sm:text-xs font-black tracking-widest text-slate-200 uppercase flex items-center gap-2 group-hover:text-white transition-colors">
         <span className="w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full bg-theme-accent animate-pulse"></span>
         Página {currentPage}
      </div>

      {hasNextPage ? (
        <Link 
          href={`/?lang=${lang}&page=${currentPage + 1}`}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-800 hover:bg-theme-accent text-slate-300 hover:text-white transition-colors shadow-inner"
          aria-label="Próxima Página"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7"></path></svg>
        </Link>
      ) : (
        <div className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-800/30 text-slate-700 cursor-not-allowed">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7"></path></svg>
        </div>
      )}
      
    </div>
  );
}
