'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import SearchBar from '@/components/blog/SearchBar';
import LogoEasterEgg from '@/components/blog/LogoEasterEgg';
import ThemeToggle from '@/components/ui/ThemeToggle';

export default function NavbarMaster({ blog, categories, lang, domain }: any) {
  const [scrolled, setScrolled] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      setScrolled(currentScrollY > 20);
      
      const scrollHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
      const progress = scrollHeight > 0 ? (currentScrollY / scrollHeight) * 100 : 0;
      setScrollProgress(progress);
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const primary = blog.primaryColor || '#06b6d4';
  const secondary = blog.secondaryColor || '#3b82f6';

  return (
    <nav className={`sticky top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'glass-panel border-b border-white/5 shadow-[0_4px_30px_rgba(0,0,0,0.3)] py-2' : 'bg-theme-bg/50 backdrop-blur-sm border-b border-theme-border py-2 sm:py-4'}`}>
      {/* SCROLL INDICATOR BAR (Passo 11) */}
      <div 
        className="absolute bottom-0 left-0 h-[2px] bg-theme-accent transition-all duration-150 ease-out z-50 shadow-[0_0_10px_rgba(var(--theme-accent-rgb),0.8)]"
        style={{ width: `${scrollProgress}%` }}
      />
      
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 flex justify-between items-center gap-3 sm:gap-4">
        
        {/* LOGO & IDENTIDADE */}
        <Link href={`/?lang=${lang}`} className="flex items-center gap-2 sm:gap-3 shrink-0 group relative">
          <LogoEasterEgg>
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-10 max-w-[160px] object-contain group-hover:scale-105 transition-transform drop-shadow-xl relative z-10" />
            ) : (
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center font-black text-white text-2xl shadow-xl group-hover:-rotate-3 transition-all relative z-10" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                {blog.name?.charAt(0) || 'P'}
              </div>
            )}
          </LogoEasterEgg>
          <div className="flex flex-col relative z-10">
            <span className="font-black text-xl md:text-2xl tracking-tight text-white uppercase group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-slate-400 transition-all">
              {blog.name}
            </span>
            <span className="text-[10px] font-bold uppercase tracking-[0.3em] text-theme-accent font-mono -mt-1 opacity-80">
              {blog.niche || 'Portal Autônomo'}
            </span>
          </div>
        </Link>

        {/* LINKS EM CASCATA & INSTITUCIONAIS */}
        <div className="hidden lg:flex gap-6 items-center bg-black/20 px-6 py-2.5 rounded-full border border-white/5 shadow-inner relative z-50">
          
          {/* CASCATA (DROPDOWN DE CATEGORIAS) */}
          <div className="relative group cursor-pointer">
            <div className="flex items-center gap-1.5 text-xs font-black uppercase tracking-widest text-slate-300 group-hover:text-theme-accent transition-all">
              Categorias <span>▼</span>
            </div>
            
            {/* Menu Escondido (Cascata) */}
            <div className="absolute top-full left-0 mt-4 w-56 bg-slate-900 border border-slate-700/50 rounded-2xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all transform translate-y-2 group-hover:translate-y-0 overflow-hidden flex flex-col">
              {categories?.length > 0 ? categories.map((cat: any) => (
                <Link prefetch={false} key={cat.slug} href={`/category/${cat.slug}`} className="px-5 py-3 text-xs font-bold uppercase tracking-wider text-slate-300 hover:text-white hover:bg-slate-800 transition-colors border-b border-slate-800/50 last:border-0">
                  {cat.name}
                </Link>
              )) : (
                <div className="px-5 py-3 text-xs text-slate-500">Sem categorias</div>
              )}
            </div>
          </div>

          <span className="w-px h-4 bg-slate-700/50" />
          
          <Link href="/about" className="text-xs font-black uppercase tracking-widest text-slate-300 hover:text-white transition-all">Sobre Nós</Link>
          <Link href="/contact" className="text-xs font-black uppercase tracking-widest text-slate-300 hover:text-white transition-all">Contato</Link>
        </div>

        {/* AÇÕES E IDIOMAS */}
        <div className="flex items-center gap-4">
          <div className="hidden md:flex gap-1 bg-black/40 p-1.5 rounded-2xl border border-white/10 shadow-inner">
            {['pt', 'en', 'es'].map((l) => (
              <Link key={l} href={`/?lang=${l}`} className={`px-2.5 py-1.5 rounded-xl text-xs font-bold transition-all ${lang === l ? 'bg-theme-accent text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-white/10'}`}>
                {l.toUpperCase()}
              </Link>
            ))}
          </div>
          
          <div className="hidden sm:block">
            <SearchBar domain={domain} lang={lang} />
          </div>

          <ThemeToggle />

          <Link href="/admin" className="hidden lg:inline-flex items-center gap-2 text-[10px] uppercase font-black bg-white/5 hover:bg-slate-700 text-slate-400 hover:text-white px-3 py-2 rounded-xl border border-white/10 transition-all">
            ⚙️
          </Link>

          {/* HAMBURGER BUTTON (MOBILE) */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="lg:hidden p-2 text-theme-text hover:text-theme-accent transition-colors"
            aria-label="Toggle Mobile Menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* MOBILE MENU OVERLAY */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 z-[100] bg-theme-bg/95 backdrop-blur-xl flex flex-col pt-20 px-6 animate-in fade-in duration-200">
          <button 
            onClick={() => setIsMobileMenuOpen(false)}
            className="absolute top-6 right-6 p-2 text-theme-text hover:text-theme-accent"
          >
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <div className="flex flex-col gap-6 text-center overflow-y-auto pb-20">
            {/* Mobile Search */}
            <div className="w-full sm:hidden">
              <SearchBar domain={domain} lang={lang} />
            </div>

            <div className="w-full h-px bg-theme-border/50" />
            
            {/* Categorias Mobile */}
            <h3 className="text-xs font-black uppercase tracking-widest text-theme-accent">Categorias</h3>
            <div className="flex flex-col gap-4">
              {categories?.length > 0 ? categories.map((cat: any) => (
                <Link key={cat.slug} onClick={() => setIsMobileMenuOpen(false)} href={`/category/${cat.slug}`} className="text-lg font-bold text-theme-text hover:text-theme-accent transition-colors">
                  {cat.name}
                </Link>
              )) : (
                <span className="text-sm text-slate-500">Sem categorias</span>
              )}
            </div>

            <div className="w-full h-px bg-theme-border/50" />

            {/* Links Institucionais Mobile */}
            <h3 className="text-xs font-black uppercase tracking-widest text-theme-accent">Portal</h3>
            <Link onClick={() => setIsMobileMenuOpen(false)} href="/about" className="text-lg font-bold text-theme-text hover:text-theme-accent">Sobre Nós</Link>
            <Link onClick={() => setIsMobileMenuOpen(false)} href="/contact" className="text-lg font-bold text-theme-text hover:text-theme-accent">Contato</Link>

            <div className="w-full h-px bg-theme-border/50" />

            {/* Idiomas Mobile */}
            <h3 className="text-xs font-black uppercase tracking-widest text-theme-accent">Idioma</h3>
            <div className="flex justify-center gap-4">
              {['pt', 'en', 'es'].map((l) => (
                <Link key={l} onClick={() => setIsMobileMenuOpen(false)} href={`/?lang=${l}`} className={`px-4 py-2 rounded-xl text-sm font-bold uppercase transition-all ${lang === l ? 'bg-theme-accent text-white' : 'bg-black/20 text-slate-400'}`}>
                  {l}
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
