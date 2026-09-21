'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface HistoryItem {
  slug: string;
  title: string;
  domain: string;
  timestamp: number;
}

export default function ReadingHistory({ domain = '' }: { domain?: string }) {
  const [history, setHistory] = useState<HistoryItem[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('reading_history');
      if (stored) {
        const parsed: HistoryItem[] = JSON.parse(stored);
        // Filtrar apenas o domínio atual e os 3 mais recentes
        const domainHistory = parsed
          .filter(item => !domain || item.domain === domain)
          .sort((a, b) => b.timestamp - a.timestamp)
          .slice(0, 3);
        setHistory(domainHistory);
      }
    } catch (e) {
      console.error('Erro ao ler histórico', e);
    }
  }, [domain]);

  if (history.length === 0) return null;

  return (
    <div className="bg-theme-surface/80 backdrop-blur-md p-6 rounded-2xl border border-theme-border/60 shadow-xl">
      <h3 className="text-theme-text font-black mb-6 uppercase tracking-widest text-sm flex items-center gap-2">
        <span className="w-2 h-4 bg-indigo-500 rounded-sm inline-block"></span>
        Seu Histórico
      </h3>
      <div className="space-y-4">
        {history.map((item, i) => (
          <Link key={i} href={`/blog/${item.slug}`} className="flex flex-col group">
            <span className="text-xs text-theme-muted mb-1 font-semibold uppercase">
              {new Date(item.timestamp).toLocaleDateString('pt-BR')}
            </span>
            <h4 className="text-sm font-semibold text-slate-300 group-hover:text-theme-accent transition-colors line-clamp-2 leading-relaxed">
              {item.title}
            </h4>
          </Link>
        ))}
      </div>
      <button 
        onClick={() => {
          localStorage.removeItem('reading_history');
          setHistory([]);
        }}
        className="mt-6 text-[10px] uppercase font-bold text-slate-500 hover:text-red-400 transition-colors tracking-widest w-full text-left"
      >
        Limpar Histórico
      </button>
    </div>
  );
}
