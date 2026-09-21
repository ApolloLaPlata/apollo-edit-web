// ────────────────────────────────────────────────────────────
// Template 1: MAGAZINE HERO (Jornalismo Premium & Notícias)
// Nicho: Jornalismo, política, economia, notícias gerais
// Fontes: Playfair Display (títulos) + Inter (corpo)
// Layout: Hero cinematográfico de luxo + Grid 3 colunas editorial + Sidebar clássica
// Design Refatorado: Ultra Premium, Glassmorphism, Micro-animações e Alto Engajamento
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
import NavbarMaster from '@/components/ui/NavbarMaster';
import ScrollReveal from '@/components/blog/ScrollReveal';

export default function MagazineHeroTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#06b6d4';
  const secondary = blog.secondaryColor || '#3b82f6';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500" style={{ fontFamily: "'Inter', sans-serif" }}>
      {/* Google Fonts & Custom Utilities */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Inter:wght@400;500;600;700;800;900&display=swap');
        .magazine-serif { font-family: 'Playfair Display', serif; }
        .glass-card { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
      `}</style>

      {/* ── TOPBAR BREAKING NEWS ── */}
      <div className="w-full py-2 px-4 text-center text-xs font-black uppercase tracking-[0.2em] text-white shadow-md flex items-center justify-center gap-2" style={{ background: `linear-gradient(90deg, ${primary}, ${secondary})` }}>
        <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
        <span>⚡ COBERTURA EDITORIAL EM TEMPO REAL • REDAÇÃO ESPECIALIZADA</span>
      </div>

      {/* ── NAVBAR PREMIUM GLASSMORPHISM ── */}
      <NavbarMaster blog={blog} categories={categories} lang={lang} domain={domain} />

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── CONTEÚDO PRINCIPAL (12 COLUNAS) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

          {/* COLUNA PRINCIPAL (8 col) */}
          <div className="lg:col-span-8 space-y-12">

            {/* HERO CINEMATOGRÁFICO DE LUXO */}
            {heroPost && (
              <ScrollReveal>
                <article className="glass-card group relative h-[500px] md:h-[600px]">
                  <Link href={`/blog/${heroPost.slug}`} className="absolute inset-0 z-0">
                  {heroPost.coverImage ? (
                    <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[2000ms] ease-out" loading="eager" fetchPriority="high" />
                  ) : (
                    <div className="w-full h-full" style={{ background: `linear-gradient(135deg, #0f172a, ${primary}50)` }} />
                  )}
                </Link>
                
                {/* Gradiente de profundidade */}
                <div className="absolute inset-0 z-10 bg-gradient-to-t from-black via-black/60 to-transparent opacity-90 group-hover:opacity-80 transition-opacity" />
                
                {/* Badges superiores */}
                <div className="absolute top-6 left-6 z-20 flex items-center gap-2.5">
                  <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest text-white shadow-lg backdrop-blur-md" style={{ backgroundColor: primary }}>
                    📌 Manchete Principal
                  </span>
                  {heroPost.category && (
                    <span className="px-3.5 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-black/60 text-slate-200 backdrop-blur-md border border-white/10">
                      {heroPost.category}
                    </span>
                  )}
                </div>

                {/* Conteúdo sobreposto */}
                <div className="absolute bottom-0 left-0 right-0 z-20 p-8 md:p-12 space-y-4">
                  <div className="flex items-center gap-3 text-xs text-slate-300 font-mono font-bold">
                    <span>✍️ Por <strong className="text-white">{heroPost.author}</strong></span>
                    <span>•</span>
                    <span>📅 {fmtDate(heroPost.createdAt)}</span>
                  </div>

                  <Link href={`/blog/${heroPost.slug}`}>
                    <h1 className="text-3xl sm:text-5xl font-black text-white leading-tight magazine-serif group-hover:text-cyan-400 transition-colors">
                      {heroPost.title}
                    </h1>
                  </Link>

                  <p className="text-slate-300 text-sm sm:text-base line-clamp-3 leading-relaxed max-w-3xl font-normal">
                    {cleanExcerpt(heroPost.contentMd, 260)}...
                  </p>

                  <div className="pt-3 flex items-center justify-between border-t border-white/10">
                    <Link
                      href={`/blog/${heroPost.slug}`}
                      className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-extrabold text-xs uppercase tracking-wider text-white shadow-xl transition-all hover:scale-105 active:scale-95"
                      style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
                    >
                      <span>Ler Reportagem Completa</span>
                      <span>→</span>
                    </Link>

                    <span className="text-xs font-bold text-slate-400 font-mono hidden sm:inline-block">
                      ⏱️ ~{Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} min de leitura
                    </span>
                  </div>
                </div>
              </article>
              </ScrollReveal>
            )}

            {/* SEÇÃO: COBERTURA EDITORIAL */}
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-theme-border/80 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-8 rounded-full shadow-sm" style={{ backgroundColor: primary }} />
                  <div>
                    <h2 className="text-xl sm:text-2xl font-black text-theme-text uppercase tracking-tight magazine-serif">
                      Edição Contínua & Reportagens
                    </h2>
                    <p className="text-xs text-theme-muted font-medium">Análises detalhadas redigidas pela Equipe de Jornalistas</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-theme-muted bg-theme-surface px-3 py-1.5 rounded-lg border border-theme-border">
                  {otherPosts.length} Artigos
                </span>
              </div>

              <div className="w-full">
                <AdBanner type="horizontal" domain={domain} />
              </div>

              {/* GRID 2 COLUNAS PREMIUM */}
              {otherPosts.length === 0 ? (
                <div className="py-16 text-center bg-theme-surface/50 rounded-3xl border border-dashed border-theme-border p-8">
                  <span className="text-4xl block mb-3">📰</span>
                  <h3 className="font-bold text-base text-theme-text">Nenhuma outra reportagem no momento</h3>
                  <p className="text-xs text-theme-muted mt-1">O enxame editorial está redigindo novas matérias para esta edição.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                  {otherPosts.map((post, idx) => (
                    <ScrollReveal key={post.id} delay={idx * 0.1}>
                      <article className="glass-card group flex flex-col justify-between h-full">
                        <div className="flex flex-col h-full">
                          {/* Imagem do Card */}
                          <Link href={`/blog/${post.slug}`} className="block relative h-48 w-full overflow-hidden">
                          {post.coverImage ? (
                            <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" loading="lazy" />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #1e293b, ${primary}30)` }}>
                              <span className="text-3xl opacity-30">📰</span>
                            </div>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
                          
                          {post.category && (
                            <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider bg-black/70 text-white backdrop-blur-md border border-white/10">
                              {post.category}
                            </span>
                          )}
                        </Link>

                        {/* Conteúdo do Card */}
                        <div className="p-5 space-y-2.5">
                          <div className="flex items-center justify-between text-[10px] text-theme-muted font-mono font-bold">
                            <span>📅 {fmtDate(post.createdAt)}</span>
                            <span>⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                          </div>

                          <Link href={`/blog/${post.slug}`}>
                            <h3 className="font-bold text-lg text-theme-text leading-snug line-clamp-2 magazine-serif group-hover:text-primary transition-colors">
                              {post.title}
                            </h3>
                          </Link>

                          <p className="text-xs text-theme-muted line-clamp-2 leading-relaxed font-normal">
                            {cleanExcerpt(post.contentMd, 120)}...
                          </p>
                        </div>
                      </div>

                      {/* Rodapé do Card */}
                      <div className="px-5 py-3.5 bg-theme-bg/50 border-t border-theme-border/60 flex items-center justify-between text-[11px] font-extrabold">
                        <span className="text-theme-muted truncate max-w-[140px]">✍️ {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                        <Link href={`/blog/${post.slug}`} className="text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                          <span>Ler</span>
                          <span>→</span>
                        </Link>
                      </div>
                      </article>
                    </ScrollReveal>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* COLUNA DA DIREITA: SIDEBAR (4 col) */}
          <aside className="lg:col-span-4 space-y-8 sticky top-24">
            
            {/* WIDGET 1: SOBRE A EDIÇÃO */}
            <div className="glass-panel rounded-3xl p-6 space-y-4 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-cyan-500/10 via-blue-500/5 to-transparent rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shadow-md" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                  🗞️
                </div>
                <div>
                  <h3 className="font-extrabold text-base text-theme-text uppercase tracking-tight magazine-serif">Redação VIP</h3>
                  <p className="text-xs text-theme-muted font-mono">Cobertura 24 horas por dia</p>
                </div>
              </div>
              <p className="text-xs text-theme-muted leading-relaxed font-normal">
                {blog.description || `O ${blog.name} produz jornalismo investigativo e relatórios técnicos contínuos sem interferência humana.`}
              </p>
              <div className="pt-2 border-t border-theme-border/60 flex items-center justify-between text-[11px] font-bold font-mono text-theme-muted">
                <span>Edição: <strong className="text-emerald-400">● Ao Vivo</strong></span>
                <span>Artigos: <strong className="text-theme-text">{allPosts.length}+</strong></span>
              </div>
            </div>

            {/* WIDGET 2: ANÚNCIO SIDEBAR */}
            <div className="w-full">
              <AdBanner type="sidebar" domain={domain} />
            </div>

            {/* WIDGET 3: NEWSLETTER */}
            <div className="glass-panel rounded-3xl p-6">
              <NewsletterWidget blogId={String(blog.id)} />
            </div>

            {/* WIDGET 4: HISTÓRICO */}
            <div className="glass-panel rounded-3xl p-6">
              <ReadingHistory />
            </div>

            {/* WIDGET 5: CATEGORIAS */}
            <div className="glass-panel rounded-3xl p-6 space-y-3">
              <h3 className="font-extrabold text-sm text-theme-text uppercase tracking-wider pb-2 border-b border-theme-border magazine-serif">
                📂 Cadernos Editoriais
              </h3>
              <div className="flex flex-wrap gap-2 pt-1">
                {categories.map((cat) => (
                  <Link
                    key={cat.slug}
                    href={`/category/${cat.slug}`}
                    className="px-3 py-1.5 rounded-xl bg-theme-bg hover:bg-theme-border/60 text-theme-muted hover:text-theme-text text-xs font-bold transition-all border border-theme-border"
                  >
                    {cat.name}
                  </Link>
                ))}
              </div>
            </div>

          </aside>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
