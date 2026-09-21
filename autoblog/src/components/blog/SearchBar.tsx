'use client';
import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

interface SearchResult {
  id: string;
  title: string;
  slug: string;
  coverImage?: string;
  createdAt: string;
  blogDomain?: string;
}

interface SearchBarProps {
  domain: string;
  lang?: string;
}

export default function SearchBar({ domain, lang = 'pt' }: SearchBarProps) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Fecha ao clicar fora
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
        setQuery('');
        setResults([]);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Abre com Ctrl+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
        setTimeout(() => inputRef.current?.focus(), 100);
      }
      if (e.key === 'Escape') {
        setOpen(false);
        setQuery('');
        setResults([]);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  // Debounce da busca
  useEffect(() => {
    if (query.length < 2) { setResults([]); return; }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(query)}&lang=${lang}`);
        const data = await res.json();
        if (data.success) setResults(data.posts || []);
      } catch {}
      setLoading(false);
    }, 300);
    return () => clearTimeout(timer);
  }, [query, lang]);

  return (
    <div ref={containerRef} className="relative">
      {/* Botão Lupa */}
      <button
        onClick={() => { setOpen(true); setTimeout(() => inputRef.current?.focus(), 100); }}
        className="flex items-center gap-2 bg-slate-800/60 hover:bg-slate-700/80 border border-slate-700 hover:border-slate-500 text-slate-400 hover:text-white px-3 py-1.5 rounded-lg text-sm transition-all group"
        title="Buscar (Ctrl+K)"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <span className="hidden sm:block text-xs">Buscar</span>
        <kbd className="hidden sm:block text-[10px] bg-slate-700 px-1.5 py-0.5 rounded border border-slate-600 group-hover:border-slate-500">⌘K</kbd>
      </button>

      {/* Modal de Busca */}
      {open && (
        <div className="fixed inset-0 z-[9999] flex items-start justify-center pt-20 px-4">
          {/* Overlay */}
          <div className="absolute inset-0 bg-theme-bg/80 backdrop-blur-xl" onClick={() => { setOpen(false); setQuery(''); setResults([]); }} />
          
          {/* Painel */}
          <div className="relative w-full max-w-2xl bg-theme-surface/70 backdrop-blur-3xl border border-theme-border/60 rounded-3xl shadow-2xl overflow-hidden mt-10">
            <div className="absolute top-0 right-0 w-64 h-64 bg-theme-accent/5 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none" />
            {/* Input */}
            <div className="flex items-center gap-4 px-6 py-5 border-b border-theme-border/50 bg-black/20 relative z-10">
              <svg className="w-6 h-6 text-theme-accent flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="Busque por relatórios, análises, artigos..."
                className="flex-1 bg-transparent text-theme-text text-xl font-medium outline-none placeholder:text-theme-muted/50 focus:placeholder:text-theme-muted/30 transition-colors"
                autoComplete="off"
              />
              {loading && (
                <div className="w-5 h-5 border-2 border-theme-accent border-t-transparent rounded-full animate-spin flex-shrink-0" />
              )}
              <kbd onClick={() => { setOpen(false); setQuery(''); setResults([]); }} className="text-[10px] bg-theme-surface px-2.5 py-1.5 rounded-lg border border-theme-border/50 text-theme-muted font-bold cursor-pointer hover:text-white hover:border-theme-accent transition-all shadow-inner tracking-widest uppercase">ESC</kbd>
            </div>

            {/* Resultados */}
            <div className="max-h-[60vh] overflow-y-auto relative z-10 custom-scrollbar">
              {results.length === 0 && query.length >= 2 && !loading && (
                <div className="px-6 py-16 text-center text-theme-muted">
                  <div className="text-5xl mb-4 opacity-50 filter grayscale">🔍</div>
                  <p className="text-lg font-medium">Nenhum resultado neural para "<strong className="text-theme-text">{query}</strong>"</p>
                </div>
              )}
              {results.length === 0 && query.length < 2 && (
                <div className="px-6 py-10 text-theme-muted text-sm text-center">
                  <p className="font-black mb-2 text-theme-text uppercase tracking-widest text-xs opacity-50">Inteligência Ativa</p>
                  <p>Digite pelo menos 2 caracteres para vasculhar o banco de dados do portal.</p>
                </div>
              )}
              {results.map((post) => (
                <Link
                  key={post.id}
                  href={`/blog/${post.slug}?lang=${lang}`}
                  onClick={() => { setOpen(false); setQuery(''); setResults([]); }}
                  className="flex items-center gap-5 px-6 py-4 hover:bg-black/20 transition-all border-b border-theme-border/30 last:border-0 group"
                >
                  {post.coverImage ? (
                    <img src={post.coverImage} alt="" className="w-20 h-14 object-cover rounded-xl flex-shrink-0 bg-slate-900 border border-theme-border/50 group-hover:border-theme-accent/50 transition-colors" />
                  ) : (
                    <div className="w-20 h-14 rounded-xl bg-slate-900 border border-theme-border/50 flex items-center justify-center flex-shrink-0 group-hover:border-theme-accent/50 transition-colors">
                      <span className="opacity-20 text-xl">📄</span>
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-theme-text font-black text-sm leading-snug line-clamp-2 group-hover:text-theme-accent transition-colors">{post.title}</p>
                    <p className="text-theme-accent/80 font-bold text-[10px] mt-1.5 uppercase tracking-widest">
                      {new Date(post.createdAt).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-theme-muted group-hover:text-theme-accent transition-colors flex-shrink-0 transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              ))}
            </div>

            {/* Footer */}
            {results.length > 0 && (
              <div className="px-6 py-4 border-t border-theme-border/60 bg-black/40 text-[10px] text-theme-muted font-bold tracking-widest uppercase flex justify-between relative z-10">
                <span>{results.length} resultado{results.length !== 1 ? 's' : ''} indexado{results.length !== 1 ? 's' : ''}</span>
                <span className="hidden sm:block">↑↓ Navegar · ↵ Acessar</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
