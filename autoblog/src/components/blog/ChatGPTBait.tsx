'use client';

import React from 'react';

interface ChatGPTBaitProps {
  domain: string;
  slug: string;
  title: string;
}

export default function ChatGPTBait({ domain, slug, title }: ChatGPTBaitProps) {
  // Constrói a URL do artigo
  const articleUrl = `https://${domain}/blog/${slug}`;
  
  // Constrói o Prompt encriptado na URL do ChatGPT
  const promptText = `Por favor, ative a navegação web, acesse este link e faça um resumo executivo dos 3 principais pontos do artigo "${title}": ${articleUrl}`;
  const chatGptUrl = `https://chatgpt.com/?q=${encodeURIComponent(promptText)}`;

  return (
    <div className="bg-gradient-to-r from-slate-900 to-slate-800 border border-emerald-500/30 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-2xl mb-12 relative overflow-hidden group">
      
      {/* Background Effect */}
      <div className="absolute inset-0 bg-emerald-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
      
      {/* Icon & Text */}
      <div className="flex items-center gap-6 z-10">
        <div className="w-16 h-16 shrink-0 bg-emerald-500/10 rounded-full flex items-center justify-center border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
          <svg className="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <div className="text-center md:text-left">
          <h3 className="text-xl md:text-2xl font-black text-white mb-2 tracking-tight">Sem tempo para ler tudo?</h3>
          <p className="text-slate-400 font-medium text-sm md:text-base leading-relaxed">
            Nós facilitamos para você. Peça para o <strong className="text-emerald-400">ChatGPT</strong> ler esta página e extrair um resumo de 30 segundos!
          </p>
        </div>
      </div>

      {/* CTA Button */}
      <div className="w-full md:w-auto shrink-0 z-10">
        <a 
          href={chatGptUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="flex items-center justify-center gap-2 w-full md:w-auto bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-8 py-4 rounded-xl shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_rgba(16,185,129,0.6)] hover:-translate-y-1 transition-all duration-300 group-hover:scale-105"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          Resumir com ChatGPT
        </a>
      </div>
      
    </div>
  );
}
