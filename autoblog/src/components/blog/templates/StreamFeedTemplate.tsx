// ────────────────────────────────────────────────────────────
// Template 2: STREAM FEED (Música, Cultura & Entretenimento Premium)
// Nicho: Música, entretenimento, cultura pop, estilo de vida
// Fontes: DM Sans (corpo) + DM Serif Display (títulos)
// Layout: Banner de Identidade Spotify/Apple Music + Feed de Cards Horizontais
// Design Refatorado: Ultra Vibrante, Glassmorphism Profundo, Neon e Micro-animações
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

export default function StreamFeedTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#ec4899';
  const secondary = blog.secondaryColor || '#a855f7';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500" style={{ fontFamily: "'DM Sans', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;800&family=DM+Serif+Display:ital@0;1&display=swap');
        .stream-serif { font-family: 'DM Serif Display', serif; }
      `}</style>

      {/* ── TOPBAR NEON ── */}
      <div className="w-full py-2 px-4 text-center text-xs font-black uppercase tracking-widest text-white shadow-lg flex items-center justify-center gap-2" style={{ background: `linear-gradient(90deg, ${primary}, ${secondary})` }}>
        <span className="w-2 h-2 rounded-full bg-white animate-ping" />
        <span>🎵 STREAMING EDITORIAL • COBERTURA CULTURAL & ÁUDIO 24/7</span>
      </div>

      {/* ── NAVBAR PREMIUM GLASSMORPHISM ── */}
      <NavbarMaster blog={blog} categories={categories} lang={lang} domain={domain} />

      {/* ── BANNER DE IDENTIDADE (ESTILO SPOTIFY / APPLE MUSIC) ── */}
      {heroPost && (
        <div className="w-full relative overflow-hidden border-b border-theme-border/80 shadow-2xl" style={{ background: `radial-gradient(circle at 80% 20%, ${primary}35 0%, #0a0510 60%, #000000 100%)` }}>
          <div className="absolute inset-0 opacity-20 pointer-events-none">
            {heroPost.coverImage && <img src={heroPost.coverImage} alt="" className="w-full h-full object-cover blur-3xl scale-125" />}
          </div>

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16 flex flex-col md:flex-row gap-10 items-center relative z-10">
            {/* Foto Capa 3D */}
            <Link href={`/blog/${heroPost.slug}`} className="w-full md:w-96 h-64 sm:h-80 rounded-3xl overflow-hidden shadow-[0_25px_60px_rgba(0,0,0,0.8)] border-2 shrink-0 group relative" style={{ borderColor: `${primary}60` }}>
              {heroPost.coverImage ? (
                <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-slate-900"><span className="text-6xl">🎧</span></div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
              <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center text-white">
                <span className="px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest backdrop-blur-md" style={{ backgroundColor: primary }}>
                  🔥 Destaque da Edição
                </span>
                <span className="text-xs font-mono font-bold">⏱️ 4 min</span>
              </div>
            </Link>

            {/* Detalhes do Destaque */}
            <div className="flex-1 space-y-4">
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full animate-ping" style={{ backgroundColor: primary }} />
                <span className="text-xs font-black uppercase tracking-[0.25em]" style={{ color: primary }}>Top Track Editorial</span>
                {heroPost.category && <span className="text-xs font-bold text-slate-400">/ {heroPost.category}</span>}
              </div>

              <Link href={`/blog/${heroPost.slug}`}>
                <h1 className="text-3xl sm:text-5xl font-black leading-tight text-white stream-serif hover:opacity-90 transition-opacity">
                  {heroPost.title}
                </h1>
              </Link>

              <p className="text-slate-300 text-sm sm:text-base line-clamp-3 leading-relaxed max-w-2xl font-normal">
                {cleanExcerpt(heroPost.contentMd, 260)}...
              </p>

              <div className="pt-4 flex items-center gap-4 flex-wrap">
                <Link
                  href={`/blog/${heroPost.slug}`}
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl font-extrabold text-xs uppercase tracking-wider text-white shadow-2xl transition-all hover:scale-105 active:scale-95"
                  style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
                >
                  <span>🎧 Ouvir / Ler Análise</span>
                  <span>→</span>
                </Link>
                <span className="text-xs text-slate-400 font-mono font-bold">✍️ Por {heroPost.author} • 📅 {fmtDate(heroPost.createdAt)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── CONTEÚDO PRINCIPAL (12 COLUNAS) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

          {/* COLUNA DA ESQUERDA: FEED EDITORIAL DE CARDS HORIZONTAIS (8 col) */}
          <div className="lg:col-span-8 space-y-8">
            <div className="flex items-center justify-between border-b border-theme-border/80 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-2 h-8 rounded-full shadow-sm" style={{ backgroundColor: primary }} />
                <div>
                  <h2 className="text-xl sm:text-2xl font-black text-theme-text uppercase tracking-tight stream-serif">
                    Feed de Críticas & Lançamentos
                  </h2>
                  <p className="text-xs text-theme-muted font-medium">Fluxo contínuo de cultura pop e entretenimento em áudio</p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold text-theme-muted bg-theme-surface px-3 py-1.5 rounded-lg border border-theme-border">
                {otherPosts.length} Publicações
              </span>
            </div>

            <div className="w-full">
              <AdBanner type="horizontal" domain={domain} />
            </div>

            {/* FEED DE CARDS HORIZONTAIS ESTILO PLAYLIST */}
            {otherPosts.length === 0 ? (
              <div className="py-16 text-center bg-theme-surface/50 rounded-3xl border border-dashed border-theme-border p-8">
                <span className="text-4xl block mb-3">🎵</span>
                <h3 className="font-bold text-base text-theme-text">Nenhuma outra crítica no momento</h3>
                <p className="text-xs text-theme-muted mt-1">O enxame cultural está redigindo novas matérias para este feed.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {otherPosts.map((post, index) => (
                  <article
                    key={post.id}
                    className="group bg-theme-surface/80 backdrop-blur-md shape-organic p-4 border border-theme-border shadow-md hover:shadow-2xl hover:border-primary/60 hover:-translate-y-1 transition-all duration-300 flex flex-col sm:flex-row gap-5 items-center justify-between"
                  >
                    {/* Número do ranking / Miniatura */}
                    <div className="flex items-center gap-4 w-full sm:w-auto">
                      <span className="text-lg font-black font-mono w-6 text-center text-theme-muted group-hover:text-primary transition-colors">
                        {(index + 1).toString().padStart(2, '0')}
                      </span>
                      <Link href={`/blog/${post.slug}`} className="w-24 h-24 sm:w-28 sm:h-24 rounded-xl overflow-hidden bg-slate-900 shrink-0 relative">
                        {post.coverImage ? (
                          <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-slate-800"><span className="text-2xl">🎶</span></div>
                        )}
                        {post.category && (
                          <span className="absolute bottom-1 left-1 px-1.5 py-0.5 rounded text-[8px] font-black uppercase bg-black/80 text-white">
                            {post.category}
                          </span>
                        )}
                      </Link>

                      {/* Título & Resumo */}
                      <div className="flex-1 min-w-0 sm:max-w-md space-y-1">
                        <div className="flex items-center gap-2 text-[10px] text-theme-muted font-mono font-bold">
                          <span>📅 {fmtDate(post.createdAt)}</span>
                          <span>•</span>
                          <span>✍️ {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                        </div>
                        <Link href={`/blog/${post.slug}`}>
                          <h3 className="font-bold text-base text-theme-text leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                            {post.title}
                          </h3>
                        </Link>
                        <p className="text-xs text-theme-muted line-clamp-1 font-normal">
                          {cleanExcerpt(post.contentMd, 100)}...
                        </p>
                      </div>
                    </div>

                    {/* Botão de Ação Direita */}
                    <div className="w-full sm:w-auto flex sm:flex-col items-center sm:items-end justify-between sm:justify-center gap-2 pt-3 sm:pt-0 border-t sm:border-t-0 border-theme-border/40 shrink-0">
                      <span className="text-[10px] font-mono font-bold text-theme-muted">⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                      <Link
                        href={`/blog/${post.slug}`}
                        className="px-4 py-2 rounded-xl text-xs font-extrabold uppercase tracking-wider text-white shadow transition-all hover:scale-105 active:scale-95"
                        style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
                      >
                        Ler Crítica →
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>

          {/* COLUNA DA DIREITA: SIDEBAR CULTURAL (4 col) */}
          <aside className="lg:col-span-4 space-y-8 sticky top-24">
            
            {/* WIDGET 1: HUB CULTURAL */}
            <div className="bg-theme-surface rounded-3xl p-6 border border-theme-border shadow-xl space-y-4 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-pink-500/10 via-purple-500/5 to-transparent rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shadow-md" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                  🎙️
                </div>
                <div>
                  <h3 className="font-extrabold text-base text-theme-text uppercase tracking-tight stream-serif">Cultura & Áudio Pro</h3>
                  <p className="text-xs text-theme-muted font-mono">Curadoria independente 24/7</p>
                </div>
              </div>
              <p className="text-xs text-theme-muted leading-relaxed font-normal">
                {blog.description || `O ${blog.name} monitora tendências musicais, áudio imersivo e entretenimento cultural em tempo real.`}
              </p>
              <div className="pt-2 border-t border-theme-border/60 flex items-center justify-between text-[11px] font-bold font-mono text-theme-muted">
                <span>Transmissão: <strong className="text-emerald-400">● Live Stream</strong></span>
                <span>Faixas: <strong className="text-theme-text">{allPosts.length}+</strong></span>
              </div>
            </div>

            {/* WIDGET 2: ANÚNCIO SIDEBAR */}
            <div className="w-full">
              <AdBanner type="sidebar" domain={domain} />
            </div>

            {/* WIDGET 3: NEWSLETTER */}
            <div className="bg-theme-surface rounded-3xl p-6 border border-theme-border shadow-xl">
              <NewsletterWidget blogId={String(blog.id)} />
            </div>

            {/* WIDGET 4: HISTÓRICO */}
            <div className="bg-theme-surface rounded-3xl p-6 border border-theme-border shadow-xl">
              <ReadingHistory />
            </div>

            {/* WIDGET 5: CATEGORIAS */}
            <div className="bg-theme-surface rounded-3xl p-6 border border-theme-border shadow-xl space-y-3">
              <h3 className="font-extrabold text-sm text-theme-text uppercase tracking-wider pb-2 border-b border-theme-border stream-serif">
                📂 Playlists & Temas
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
