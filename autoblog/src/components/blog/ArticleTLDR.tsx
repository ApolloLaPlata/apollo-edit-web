'use client';
import React from 'react';

export default function ArticleTLDR({ content }: { content: string }) {
  if (!content) return null;
  
  // Extrai as linhas que são bullets (geradas pela IA)
  const points = content
    .split('\n')
    .filter(line => line.trim().startsWith('-') || line.trim().startsWith('*'))
    .map(line => line.replace(/^[-*]\s*/, '').trim());

  if (points.length === 0) return null;

  return (
    <div className="bg-gradient-to-r from-theme-accent/30 via-theme-surface to-transparent p-[1px] rounded-2xl mb-12 shadow-2xl relative overflow-hidden group">
       <div className="absolute top-0 right-0 w-64 h-64 bg-theme-accent/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none group-hover:bg-theme-accent/10 transition-colors duration-1000"></div>
       <div className="bg-theme-bg/95 backdrop-blur-xl p-8 md:p-10 rounded-[15px] relative z-10">
         <div className="flex items-center gap-4 mb-8">
            <div className="w-12 h-12 rounded-full bg-theme-accent/20 flex items-center justify-center text-theme-accent shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.3)] animate-pulse">
               <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
            </div>
            <div>
              <h3 className="text-2xl font-black text-theme-text tracking-tight">Em Resumo (TL;DR)</h3>
              <p className="text-[10px] uppercase font-bold text-theme-muted tracking-widest mt-1">Gerado por Inteligência Artificial</p>
            </div>
         </div>
         <ul className="space-y-5">
           {points.map((pt, idx) => (
             <li key={idx} className="flex gap-4 items-start group/item">
               <span className="text-theme-accent mt-1.5 text-xs bg-theme-accent/10 w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 group-hover/item:scale-110 group-hover/item:bg-theme-accent group-hover/item:text-white transition-all">
                 {idx + 1}
               </span>
               <p className="text-slate-300 font-medium leading-relaxed text-lg group-hover/item:text-white transition-colors">{pt}</p>
             </li>
           ))}
         </ul>
       </div>
    </div>
  );
}
