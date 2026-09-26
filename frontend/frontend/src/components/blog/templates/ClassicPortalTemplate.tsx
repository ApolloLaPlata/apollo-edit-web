// ────────────────────────────────────────────────────────────
// Template 0: CLASSIC PORTAL (O PADRÃO ORIGINAL)
// Nicho: Universal, Notícias, Finanças, Tecnologia, Geral
// Fontes: Inter (corpo e títulos) ou fonte configurada pelo usuário
// Layout: Hero Central Imponente + Grade Elegante 2 Colunas + Sidebar Clássica
// O Padrão Original que o Chefe considera o melhor de todos!
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
import WebStories from '@/components/blog/WebStories';
import ScrollReveal from '@/components/blog/ScrollReveal';
import ImageWithBlur from '@/components/ui/ImageWithBlur';
import InfiniteScrollLoader from '@/components/blog/InfiniteScrollLoader';

import WebStoriesFeed from '@/components/blog/WebStoriesFeed';

export default function ClassicPortalTemplate({ blog, heroPost, otherPosts, webStories, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#7c3aed';
  const secondary = blog.secondaryColor || '#1e40af';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500" style={{ fontFamily: blog.fontFamily ? undefined : "'Inter', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
        .classic-glass {
          background: rgba(15, 23, 42, 0.75);
          backdrop-filter: blur(16px);
          -webkit-backdrop-filter: blur(16px);
        }
      `}</style>

      {/* ── TOPBAR BREAKING NEWS ── */}
      <div className="w-full py-2 px-4 text-center text-xs font-extrabold uppercase tracking-widest text-white shadow-md flex items-center justify-center gap-2" style={{ background: `linear-gradient(90deg, ${primary}, ${secondary})` }}>
        <span className="w-2 h-2 rounded-full bg-white animate-ping" />
        <span>⚡ COBERTURA AO VIVO • ATUALIZADO CONTINUAMENTE PELA NOSSA REDAÇÃO</span>
      </div>

      {/* ── NAVBAR PREMIUM GLASSMORPHISM ── */}
      <NavbarMaster blog={blog} categories={categories} lang={lang} domain={domain} />

      {/* ── NEWS TICKER FLUTUANTE ── */}
      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── WEB STORIES FEED (NOVO) ── */}
      {webStories && webStories.length > 0 && (
         <WebStoriesFeed stories={webStories} primaryColor={primary} />
      )}

      {/* ── CONTEÚDO PRINCIPAL (12 COLUNAS: 8 MAIN + 4 SIDEBAR) ── */}
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-4 sm:py-8 md:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-10 items-start">

          {/* COLUNA DA ESQUERDA: HERO + GRADE DE ARTIGOS (8 col) */}
          <div className="lg:col-span-8 space-y-6 md:space-y-12">

            {/* HERO CARD CENTRAL IMPONENTE (O DESTAQUE ORIGINAL) */}
            {heroPost && (
              <ScrollReveal>
                <article className="glass-card group relative flex flex-col min-h-[320px] sm:min-h-[400px]">
                  <Link href={`/blog/${heroPost.slug}`} className="relative block h-56 sm:h-96 w-full overflow-hidden">
                  {heroPost.coverImage ? (
                    <ImageWithBlur
                      src={heroPost.coverImage}
                      alt={heroPost.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out"
                      containerClassName="w-full h-full"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #0f172a, ${primary}40)` }}>
                      <span className="text-6xl opacity-20 font-black">📰</span>
                    </div>
                  )}
                  {/* Gradiente de proteção de leitura */}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent opacity-80 group-hover:opacity-70 transition-opacity" />
                  
                  {/* Badge sobre a imagem */}
                  <div className="absolute top-6 left-6 z-10 flex items-center gap-2">
                    <span className="px-3.5 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest text-white shadow-lg backdrop-blur-md" style={{ backgroundColor: primary }}>
                      🔥 Em Destaque
                    </span>
                    {heroPost.category && (
                      <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-black/60 text-slate-200 backdrop-blur-md border border-white/10">
                        {heroPost.category}
                      </span>
                    )}
                  </div>
                </Link>

                {/* Conteúdo do Hero na parte inferior */}
                <div className="p-4 sm:p-8 sm:-mt-20 relative z-10 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center gap-2 sm:gap-3 text-[10px] sm:text-xs text-theme-muted font-mono font-bold mb-2 sm:mb-3">
                      <span>✍️ Por <strong className="text-theme-text">{heroPost.author}</strong></span>
                      <span className="hidden sm:inline">•</span>
                      <span>📅 {fmtDate(heroPost.createdAt)}</span>
                    </div>
                    
                    <Link href={`/blog/${heroPost.slug}`}>
                      <h1 className="text-xl sm:text-4xl font-black text-theme-text leading-tight mb-2 sm:mb-4 group-hover:text-primary transition-colors">
                        {heroPost.title}
                      </h1>
                    </Link>
                    
                    <p className="text-theme-muted text-xs sm:text-base leading-relaxed line-clamp-2 sm:line-clamp-3 mb-4 sm:mb-6">
                      {cleanExcerpt(heroPost.contentMd, 260)}...
                    </p>
                  </div>

                  <div className="pt-4 border-t border-theme-border/60 flex items-center justify-between">
                    <Link
                      href={`/blog/${heroPost.slug}`}
                      className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-extrabold text-xs uppercase tracking-wider text-white shadow-lg transition-all hover:scale-105 active:scale-95"
                      style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
                    >
                      <span>Ler Matéria Completa</span>
                      <span>→</span>
                    </Link>
                    
                    <span className="text-xs font-bold text-theme-muted font-mono hidden sm:inline-block">
                      ⏱️ ~{Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} min de leitura
                    </span>
                  </div>
                </div>
              </article>
              </ScrollReveal>
            )}

            {/* ANÚNCIO HORIZONTAL INTERMEDIÁRIO */}
            <div className="w-full">
              <AdBanner type="horizontal" domain={domain} />
            </div>

            {/* SEÇÃO: ÚLTIMAS PUBLICAÇÕES & ANÁLISES */}
            <div className="space-y-6">
              <div className="flex items-center justify-between border-b border-theme-border/80 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-8 rounded-full shadow-sm" style={{ backgroundColor: primary }} />
                  <div>
                    <h2 className="text-xl sm:text-2xl font-black text-theme-text uppercase tracking-tight">
                      Últimas Publicações & Análises
                    </h2>
                    <p className="text-xs text-theme-muted font-medium">Conteúdo gerado de forma contínua e revisado pela Equipe Especializada</p>
                  </div>
                </div>
                <span className="text-xs font-mono font-bold text-theme-muted bg-theme-surface px-3 py-1.5 rounded-lg border border-theme-border">
                  {otherPosts.length} Artigos
                </span>
              </div>

              {/* GRADE DE ARTIGOS (2 COLUNAS NO DESKTOP) */}
              {otherPosts.length === 0 ? (
                <div className="py-16 text-center bg-theme-surface/50 rounded-3xl border border-dashed border-theme-border p-8">
                  <span className="text-4xl block mb-3">📭</span>
                  <h3 className="font-bold text-base text-theme-text">Nenhum outro artigo no momento</h3>
                  <p className="text-xs text-theme-muted mt-1">O enxame editorial está redigindo novas matérias para este portal.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
                  {otherPosts.map((post, idx) => (
                    <ScrollReveal key={post.id} delay={idx * 0.1}>
                      <article className="glass-card group flex flex-col sm:flex-col justify-between h-full">
                        <div className="flex flex-row sm:flex-col h-full w-full">
                          {/* Imagem do Card */}
                          <Link href={`/blog/${post.slug}`} className="block relative w-[100px] h-auto sm:h-48 sm:w-full shrink-0 overflow-hidden rounded-l-lg sm:rounded-none">
                          {post.coverImage ? (
                            <ImageWithBlur
                              src={post.coverImage}
                              alt={post.title}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                              containerClassName="w-full h-full"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #1e293b, ${primary}30)` }}>
                              <span className="text-xl sm:text-3xl opacity-30">📄</span>
                            </div>
                          )}
                          <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
                          
                          {post.category && (
                            <span className="hidden sm:block absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider bg-black/70 text-white backdrop-blur-md border border-white/10">
                              {post.category}
                            </span>
                          )}
                        </Link>

                        {/* Conteúdo do Card */}
                        <div className="p-3 sm:p-5 flex flex-col justify-center flex-1 space-y-1.5 sm:space-y-2.5 w-[calc(100%-100px)] sm:w-full">
                          <div className="flex items-center justify-between text-[9px] sm:text-[10px] text-theme-muted font-mono font-bold">
                            <span>📅 {fmtDate(post.createdAt)}</span>
                            <span className="hidden sm:inline">⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                          </div>

                          <Link href={`/blog/${post.slug}`}>
                            <h3 className="font-extrabold text-sm sm:text-base text-theme-text leading-snug line-clamp-2 group-hover:text-primary transition-colors">
                              {post.title}
                            </h3>
                          </Link>

                          <p className="hidden sm:block text-xs text-theme-muted line-clamp-2 leading-relaxed font-normal">
                            {cleanExcerpt(post.contentMd, 120)}...
                          </p>
                        </div>
                      </div>

                      {/* Rodapé do Card (Escondido no mobile, exibe na horizontal sem ele) */}
                      <div className="hidden sm:flex px-5 py-3.5 bg-theme-bg/50 border-t border-theme-border/60 items-center justify-between text-[11px] font-extrabold">
                        <span className="text-theme-muted truncate max-w-[140px]">✍️ {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                        <Link href={`/blog/${post.slug}`} className="text-primary group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                          <span>Ler</span>
                          <span>→</span>
                        </Link>
                      </div>
                      </article>
                    </ScrollReveal>
                  ))}
                  
                  {/* INFINITE SCROLL */}
                  <InfiniteScrollLoader blogId={String(blog.id)} initialOffset={6} lang={lang} domain={domain} primaryColor={primary} />
                </div>
              )}
            </div>
          </div>

          {/* COLUNA DA DIREITA: SIDEBAR CLÁSSICA (4 col) */}
          <aside className="lg:col-span-4 space-y-8 sticky top-24">
            
            {/* WIDGET 1: REMOVIDO A PEDIDO DA DIREÇÃO */}            {/* WIDGET 2: ANÚNCIO SIDEBAR */}
            <div className="w-full">
              <AdBanner type="sidebar" domain={domain} />
            </div>

            {/* WIDGET 3: NEWSLETTER */}
            <div className="glass-panel rounded-3xl p-6">
              <NewsletterWidget blogId={String(blog.id)} />
            </div>

            {/* WIDGET 4: HISTÓRICO DE LEITURA DO USUÁRIO */}
            <div className="glass-panel rounded-3xl p-6">
              <ReadingHistory />
            </div>

            {/* WIDGET 5: CATEGORIAS EM DESTAQUE */}
            <div className="glass-panel rounded-3xl p-6 space-y-3">
              <h3 className="font-extrabold text-sm text-theme-text uppercase tracking-wider pb-2 border-b border-theme-border">
                📂 Categorias do Portal
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

      {/* ── FOOTER DO PORTAL ── */}
      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
