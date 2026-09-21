// ────────────────────────────────────────────────────────────
// Template 5: DASHBOARD PORTAL (Finanças, Cripto & BI Premium)
// Nicho: Finanças, criptomoedas, ações, economia, dados, BI, trading
// Fontes: IBM Plex Mono (dados e KPIs) + Inter (corpo)
// Layout: Sidenav Fixo Executivo + Ticker Financeiro + Grid BI Compacto
// Design Refatorado: V3 Premium (Glassmorphism, Dark Void, ScrollReveal)
// ────────────────────────────────────────────────────────────
import React from 'react';
import Link from 'next/link';
import { TemplateProps, cleanExcerpt, fmtDate } from './LayoutRouter';
import AdBanner from '@/components/blog/AdBanner';
import NewsletterWidget from '@/components/blog/NewsletterWidget';
import SearchBar from '@/components/blog/SearchBar';
import Footer from '@/components/blog/Footer';
import NewsTicker from '@/components/blog/NewsTicker';
import ReadingHistory from '@/components/blog/ReadingHistory';
import ScrollReveal from '@/components/blog/ScrollReveal';

export default function DashboardPortalTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#3b82f6';
  const secondary = blog.secondaryColor || '#06b6d4';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg bg-grain glow-backdrop text-theme-text transition-colors duration-500 relative" style={{ fontFamily: "'Inter', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&display=swap');
        .bi-mono { font-family: 'IBM Plex Mono', monospace; }
        :root { --color-theme-accent: ${primary}; --accent-hover: ${secondary}; }
      `}</style>

      {/* ── TOPBAR DE MERCADO (KPIS AO VIVO) ── */}
      <div className="w-full py-2 px-4 bg-black/90 backdrop-blur-xl border-b border-white/5 text-[11px] font-bold text-slate-300 bi-mono flex justify-between items-center gap-4 overflow-x-auto no-scrollbar shadow-lg z-50 relative">
        <div className="flex items-center gap-5 shrink-0">
          <span className="flex items-center gap-2 text-emerald-400 font-black tracking-widest uppercase">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping shadow-[0_0_10px_rgba(16,185,129,0.8)]" />
            MARKET_LIVE
          </span>
          <span className="opacity-80">BTC/USD <strong className="text-emerald-400 font-extrabold">+4.28%</strong></span>
          <span className="opacity-80">ETH/USD <strong className="text-emerald-400 font-extrabold">+2.91%</strong></span>
          <span className="opacity-80">S&P 500 <strong className="text-blue-400 font-extrabold">+0.85%</strong></span>
          <span className="opacity-80">NASDAQ <strong className="text-emerald-400 font-extrabold">+1.12%</strong></span>
        </div>
        <div className="shrink-0 text-slate-500 font-bold opacity-60 hover:opacity-100 transition-opacity">
          ⚡ BI AUTÔNOMO 24/7 • REDAÇÃO VIP
        </div>
      </div>

      {/* ── NAVBAR FINANCEIRA EXECUTIVA ── */}
      <nav className="w-full glass-panel sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center gap-6">
          
          {/* LOGO */}
          <Link href={`/?lang=${lang}`} className="flex items-center gap-4 shrink-0 group">
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-10 max-w-[160px] object-contain group-hover:scale-105 transition-transform duration-500" />
            ) : (
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center font-black text-white text-lg shadow-[0_0_20px_rgba(255,255,255,0.1)] group-hover:scale-110 transition-transform duration-500" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                {blog.name?.charAt(0) || 'D'}
              </div>
            )}
            <div className="flex flex-col">
              <span className="font-black text-2xl tracking-tighter text-white group-hover:opacity-90 transition-opacity">
                {blog.name}
              </span>
              <span className="text-[9px] font-bold uppercase tracking-[0.3em] text-theme-muted bi-mono -mt-1 opacity-70">
                {blog.niche || 'Finanças & Cripto'}
              </span>
            </div>
          </Link>

          {/* CATEGORIAS */}
          <div className="hidden lg:flex gap-8 items-center">
            {categories.slice(0, 6).map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="text-[11px] font-extrabold uppercase tracking-widest text-theme-muted hover:text-white transition-all relative after:absolute after:-bottom-1 after:left-0 after:w-0 after:h-0.5 after:bg-white hover:after:w-full after:transition-all after:duration-300">
                {cat.name}
              </Link>
            ))}
          </div>

          {/* AÇÕES */}
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex gap-1 bg-black/40 p-1.5 rounded-xl border border-white/10 shadow-inner">
              <Link href={`/?lang=pt`} className={`px-2.5 py-1 rounded-lg text-sm transition-all ${lang === 'pt' ? 'bg-white/10 shadow text-white' : 'opacity-40 hover:opacity-100'}`} title="Português">🇧🇷</Link>
              <Link href={`/?lang=en`} className={`px-2.5 py-1 rounded-lg text-sm transition-all ${lang === 'en' ? 'bg-white/10 shadow text-white' : 'opacity-40 hover:opacity-100'}`} title="English">🇺🇸</Link>
              <Link href={`/?lang=es`} className={`px-2.5 py-1 rounded-lg text-sm transition-all ${lang === 'es' ? 'bg-white/10 shadow text-white' : 'opacity-40 hover:opacity-100'}`} title="Español">🇪🇸</Link>
            </div>
            
            <SearchBar domain={domain} lang={lang} />
            
            <Link href="/admin" className="hidden sm:inline-flex items-center gap-1.5 text-[11px] uppercase font-black bg-white text-black hover:bg-zinc-200 px-4 py-2.5 rounded-xl shadow-[0_0_15px_rgba(255,255,255,0.2)] transition-all hover:scale-105 active:scale-95">
              <span>⚡</span> Admin
            </Link>
          </div>
        </div>
      </nav>

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── CONTEÚDO PRINCIPAL (LAYOUT DASHBOARD EXECUTIVO) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

          {/* SIDENAV EXECUTIVA / ÍNDICE RÁPIDO (3 col) */}
          <aside className="lg:col-span-3 space-y-6 sticky top-28">
            
            <ScrollReveal direction="left" delay={0.1}>
              <div className="glass-card p-6 space-y-5">
                <div className="flex items-center justify-between border-b border-white/10 pb-3">
                  <span className="font-black text-[10px] uppercase tracking-widest text-white opacity-80">📊 Índices do Portal</span>
                  <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 bi-mono shadow-[0_0_10px_rgba(16,185,129,0.1)]">24H</span>
                </div>
                <div className="space-y-3 bi-mono text-xs">
                  <div className="flex justify-between items-center p-2.5 rounded-lg bg-black/40 border border-white/5 hover:border-white/20 transition-colors">
                    <span className="text-theme-muted font-bold">Relatórios</span>
                    <strong className="text-white">{allPosts.length}</strong>
                  </div>
                  <div className="flex justify-between items-center p-2.5 rounded-lg bg-black/40 border border-white/5 hover:border-white/20 transition-colors">
                    <span className="text-theme-muted font-bold">Frequência</span>
                    <strong className="text-emerald-400">Contínua</strong>
                  </div>
                  <div className="flex justify-between items-center p-2.5 rounded-lg bg-black/40 border border-white/5 hover:border-white/20 transition-colors">
                    <span className="text-theme-muted font-bold">Precisão AI</span>
                    <strong style={{ color: primary }}>100%</strong>
                  </div>
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="left" delay={0.2}>
              <div className="glass-card p-6 space-y-4">
                <h3 className="font-black text-[10px] uppercase tracking-widest text-white opacity-80 pb-2 border-b border-white/10">
                  📂 Setores de Mercado
                </h3>
                <div className="flex flex-col gap-2 pt-1">
                  {categories.map((cat) => (
                    <Link
                      key={cat.slug}
                      href={`/category/${cat.slug}`}
                      className="flex justify-between items-center px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 text-theme-muted hover:text-white text-xs font-bold transition-all border border-transparent hover:border-white/10 group"
                    >
                      <span>{cat.name}</span>
                      <span className="bi-mono text-[10px] opacity-40 group-hover:opacity-100 group-hover:translate-x-1 transition-all">→</span>
                    </Link>
                  ))}
                </div>
              </div>
            </ScrollReveal>

            <ScrollReveal direction="left" delay={0.3}>
              <div className="glass-card p-1">
                <NewsletterWidget blogId={String(blog.id)} />
              </div>
            </ScrollReveal>

            <ScrollReveal direction="left" delay={0.4}>
              <div className="glass-card p-1">
                <ReadingHistory />
              </div>
            </ScrollReveal>
          </aside>

          {/* COLUNA CENTRAL & DIREITA: HERO DASHBOARD + WIDGETS (9 col) */}
          <div className="lg:col-span-9 space-y-12">

            {/* HERO CARD FINANCEIRO (BREAKING ANALYSIS) */}
            {heroPost && (
              <ScrollReveal direction="up" delay={0.2}>
                <article className="group relative glass-card overflow-hidden flex flex-col md:flex-row min-h-[380px]">
                  <Link href={`/blog/${heroPost.slug}`} className="relative block h-72 md:h-auto md:w-[55%] overflow-hidden bg-black shrink-0">
                    {heroPost.coverImage ? (
                      <img src={heroPost.coverImage} alt={heroPost.title} className="cover-image w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #09090b, ${primary}40)` }}>
                        <span className="text-6xl opacity-20">📈</span>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-black/90 via-black/40 to-transparent" />
                    <div className="absolute top-5 left-5 z-10">
                      <span className="px-4 py-1.5 rounded-full text-[9px] font-black uppercase tracking-widest text-black shadow-[0_0_15px_rgba(255,255,255,0.3)] backdrop-blur-md bg-white">
                        🔥 Relatório Principal
                      </span>
                    </div>
                  </Link>

                  <div className="p-8 md:p-10 flex flex-col justify-center flex-1 space-y-5 relative z-10 -mt-10 md:mt-0 bg-gradient-to-t from-black via-black md:bg-none">
                    <div>
                      <div className="flex items-center gap-3 text-[10px] text-theme-muted bi-mono font-bold mb-4 uppercase tracking-widest">
                        <span className="bg-white/10 px-2 py-1 rounded">📅 {fmtDate(heroPost.createdAt)}</span>
                        <span className="opacity-50">•</span>
                        <span className="text-white">✍️ {heroPost.author}</span>
                      </div>

                      <Link href={`/blog/${heroPost.slug}`}>
                        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white leading-[1.1] mb-4 tracking-tight group-hover:text-gradient-accent transition-all duration-300">
                          {heroPost.title}
                        </h1>
                      </Link>

                      <p className="text-theme-muted text-sm leading-relaxed line-clamp-3 font-medium opacity-80">
                        {cleanExcerpt(heroPost.contentMd, 220)}...
                      </p>
                    </div>

                    <div className="pt-6 mt-auto flex items-center justify-between">
                      <Link
                        href={`/blog/${heroPost.slug}`}
                        className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl font-black text-xs uppercase tracking-widest text-white shadow-[0_0_20px_rgba(255,255,255,0.1)] transition-all hover:scale-105 active:scale-95 bg-white/10 hover:bg-white/20 border border-white/20"
                      >
                        <span>Ler na íntegra</span>
                        <span>→</span>
                      </Link>
                      <span className="text-[10px] font-bold text-white/40 bi-mono uppercase tracking-widest">
                        ⏱️ {Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} MIN READ
                      </span>
                    </div>
                  </div>
                </article>
              </ScrollReveal>
            )}

            {/* ANÚNCIO INTERMEDIÁRIO */}
            <ScrollReveal delay={0.3}>
              <div className="w-full glass-panel p-2 rounded-2xl flex items-center justify-center">
                <AdBanner type="horizontal" domain={domain} />
              </div>
            </ScrollReveal>

            {/* GRADE COMPACTA DE ANÁLISES & MERCADO (2 COLUNAS) */}
            <div className="space-y-8">
              <ScrollReveal delay={0.4}>
                <div className="flex items-end justify-between border-b border-white/10 pb-5">
                  <div className="flex items-center gap-4">
                    <div className="w-3 h-10 rounded-full shadow-[0_0_15px_rgba(255,255,255,0.5)] bg-white" />
                    <div>
                      <h2 className="text-2xl sm:text-3xl font-black text-white uppercase tracking-tighter">
                        Feed de Mercado & Análises
                      </h2>
                      <p className="text-[11px] uppercase tracking-widest text-theme-muted font-bold mt-1 opacity-70">Monitoramento contínuo de ativos globais</p>
                    </div>
                  </div>
                  <span className="text-[10px] bi-mono uppercase tracking-widest font-black text-white bg-white/10 px-4 py-2 rounded-lg border border-white/20">
                    {otherPosts.length} Pubs
                  </span>
                </div>
              </ScrollReveal>

              {otherPosts.length === 0 ? (
                <ScrollReveal delay={0.5}>
                  <div className="py-20 text-center glass-card border-dashed border-white/20 p-10">
                    <span className="text-5xl block mb-4 animate-pulse">📊</span>
                    <h3 className="font-black text-xl text-white">Nenhuma análise no momento</h3>
                    <p className="text-sm text-theme-muted mt-2">O enxame financeiro está redigindo novos relatórios.</p>
                  </div>
                </ScrollReveal>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
                  {otherPosts.map((post, idx) => (
                    <ScrollReveal key={post.id} delay={0.2 + (idx * 0.1)} direction="up">
                      <article
                        className="group glass-card flex flex-col h-full"
                      >
                        <Link href={`/blog/${post.slug}`} className="block relative h-56 w-full overflow-hidden bg-black shrink-0">
                          {post.coverImage ? (
                            <img src={post.coverImage} alt={post.title} className="cover-image w-full h-full object-cover" loading="lazy" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #0a0a0b, ${primary}30)` }}>
                              <span className="text-4xl opacity-20">📈</span>
                            </div>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-transparent to-transparent opacity-80 group-hover:opacity-60 transition-opacity" />
                          
                          {post.category && (
                            <span className="absolute top-4 left-4 px-3 py-1.5 rounded-md text-[8px] font-black uppercase tracking-widest bg-white text-black shadow-[0_0_10px_rgba(255,255,255,0.2)]">
                              {post.category}
                            </span>
                          )}
                        </Link>

                        <div className="p-6 md:p-8 flex-1 flex flex-col justify-between space-y-4">
                          <div>
                            <div className="flex items-center justify-between text-[9px] text-theme-muted bi-mono font-bold uppercase tracking-widest mb-3 opacity-70">
                              <span>📅 {fmtDate(post.createdAt)}</span>
                              <span>⏱️ {Math.max(1, Math.ceil(post.contentMd.length / 800))} MIN</span>
                            </div>

                            <Link href={`/blog/${post.slug}`}>
                              <h3 className="font-black text-xl md:text-2xl text-white leading-[1.2] tracking-tight group-hover:text-gradient-accent transition-all duration-300 mb-3">
                                {post.title}
                              </h3>
                            </Link>

                            <p className="text-sm text-theme-muted line-clamp-2 leading-relaxed font-medium opacity-80">
                              {cleanExcerpt(post.contentMd, 120)}...
                            </p>
                          </div>

                          <div className="pt-4 border-t border-white/10 flex items-center justify-between mt-auto">
                            <span className="text-[10px] text-white/50 font-black uppercase tracking-widest truncate max-w-[140px]">✍️ {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                            <Link href={`/blog/${post.slug}`} className="text-white group-hover:translate-x-2 transition-transform inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest bg-white/10 px-3 py-1.5 rounded-md">
                              <span>Ler</span>
                              <span>→</span>
                            </Link>
                          </div>
                        </div>
                      </article>
                    </ScrollReveal>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
