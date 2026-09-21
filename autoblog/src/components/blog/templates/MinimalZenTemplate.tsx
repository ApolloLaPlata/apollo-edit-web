// ────────────────────────────────────────────────────────────
// Template 7: MINIMAL ZEN (Filosofia, Arquitetura & Design Premium)
// Nicho: Filosofia, arquitetura, design, minimalismo, estilo de vida zen
// Fontes: Inter (corpo ultralimpo) + Cormorant Garamond (títulos zen)
// Layout: Respiro Máximo Estilo Apple / Kinfolk, Sem Cards Pesados, Foco Total na Leitura
// Design Refatorado: Ultra Clean, Elegância Minimalista, Tipografia Sublime
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

export default function MinimalZenTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#10b981';
  const secondary = blog.secondaryColor || '#06b6d4';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500 font-sans">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');
        .zen-serif { font-family: 'Cormorant Garamond', serif; }
        .zen-sans { font-family: 'Inter', sans-serif; }
      `}</style>

      {/* ── TOPBAR ZEN ── */}
      <div className="w-full py-2 px-4 text-center text-[10px] font-semibold uppercase tracking-[0.3em] text-white shadow-sm zen-sans" style={{ background: `linear-gradient(90deg, #064e3b, ${primary}, #064e3b)` }}>
        <span>🧘 LEITURA LIMPA & DESIGN CONTEMPLATIVO • REDAÇÃO ESPECIALIZADA</span>
      </div>

      {/* ── NAVBAR MINIMALISTA APPLE/KINFOLK ── */}
      <nav className="w-full bg-theme-surface/90 backdrop-blur-md border-b border-theme-border/50 sticky top-0 z-50 zen-sans">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-5 flex justify-between items-center gap-6">
          
          <Link href={`/?lang=${lang}`} className="flex items-center gap-3 shrink-0 group">
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-7 max-w-[140px] object-contain group-hover:opacity-80 transition-opacity" />
            ) : (
              <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-white text-xs shadow" style={{ backgroundColor: primary }}>
                {blog.name?.charAt(0) || 'Z'}
              </div>
            )}
            <div className="flex flex-col">
              <span className="font-bold text-xl tracking-wide text-theme-text uppercase zen-serif group-hover:opacity-80 transition-opacity">
                {blog.name}
              </span>
              <span className="text-[8px] font-semibold uppercase tracking-[0.25em] text-theme-muted -mt-1">
                {blog.niche || 'Filosofia & Design'}
              </span>
            </div>
          </Link>

          <div className="hidden md:flex gap-7 items-center">
            {categories.slice(0, 5).map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="text-xs font-semibold uppercase tracking-widest text-theme-muted hover:text-theme-text transition-colors">
                {cat.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-4">
            <SearchBar domain={domain} lang={lang} />
            <Link href="/admin" className="text-[10px] uppercase font-bold text-theme-muted hover:text-theme-text transition">
              Admin
            </Link>
          </div>
        </div>
      </nav>

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── ENSAIO PRINCIPAL (ZEN HERO) ── */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-16 md:py-24 text-center space-y-8">
        {heroPost && (
          <article className="space-y-6">
            <div className="text-[10px] font-semibold uppercase tracking-[0.25em] text-emerald-500 zen-sans">
              <span>{heroPost.category || 'Ensaio Principal'}</span>
            </div>

            <Link href={`/blog/${heroPost.slug}`}>
              <h1 className="text-4xl sm:text-6xl font-normal leading-[1.1] text-theme-text hover:opacity-80 transition-opacity zen-serif">
                {heroPost.title}
              </h1>
            </Link>

            <div className="flex justify-center items-center gap-3 text-xs text-theme-muted font-normal zen-sans">
              <span>✍️ {heroPost.author}</span>
              <span>•</span>
              <span>{fmtDate(heroPost.createdAt)}</span>
              <span>•</span>
              <span>~{Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} min</span>
            </div>

            {heroPost.coverImage && (
              <Link href={`/blog/${heroPost.slug}`} className="block my-10 rounded-2xl overflow-hidden shadow-xl border border-theme-border/40 max-h-[440px] group">
                <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out" />
              </Link>
            )}

            <p className="text-lg sm:text-xl text-theme-muted leading-relaxed font-light zen-serif italic max-w-2xl mx-auto">
              "{cleanExcerpt(heroPost.contentMd, 280)}..."
            </p>

            <div className="pt-6">
              <Link
                href={`/blog/${heroPost.slug}`}
                className="inline-flex items-center gap-2 px-8 py-3.5 rounded-full font-bold text-xs uppercase tracking-widest text-theme-text bg-theme-surface hover:bg-theme-border/50 border border-theme-border shadow transition-all hover:scale-105 active:scale-95 zen-sans"
              >
                <span>Ler Ensaio</span>
                <span>→</span>
              </Link>
            </div>
          </article>
        )}
      </div>

      {/* ANÚNCIO INTERMEDIÁRIO */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pb-12">
        <AdBanner type="horizontal" domain={domain} />
      </div>

      {/* ── LISTA DE LEITURAS (CLEAN LIST APPLE STYLE) ── */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 pb-24 space-y-12">
        <div className="border-b border-theme-border/60 pb-4 text-center zen-sans">
          <h2 className="text-sm font-bold uppercase tracking-[0.25em] text-theme-muted">
            Outras Reflexões & Artigos
          </h2>
        </div>

        {otherPosts.length === 0 ? (
          <div className="py-16 text-center bg-theme-surface/30 rounded-2xl border border-dashed border-theme-border p-8 zen-sans">
            <span className="text-4xl block mb-3">🧘</span>
            <h3 className="font-bold text-base text-theme-text">Nenhuma outra leitura no momento</h3>
            <p className="text-xs text-theme-muted mt-1">O enxame contemplativo está redigindo novos ensaios para esta coleção.</p>
          </div>
        ) : (
          <div className="divide-y divide-theme-border/40 space-y-8">
            {otherPosts.map((post) => (
              <article key={post.id} className="pt-8 first:pt-0 group flex flex-col sm:flex-row gap-6 items-baseline justify-between">
                <div className="space-y-2 flex-1">
                  <div className="flex items-center gap-2 text-[10px] text-emerald-500 font-bold uppercase tracking-widest zen-sans">
                    <span>{post.category || 'Reflexão'}</span>
                    <span>•</span>
                    <span className="text-theme-muted">{fmtDate(post.createdAt)}</span>
                  </div>

                  <Link href={`/blog/${post.slug}`}>
                    <h3 className="text-2xl sm:text-3xl font-normal text-theme-text leading-snug group-hover:opacity-75 transition-opacity zen-serif">
                      {post.title}
                    </h3>
                  </Link>

                  <p className="text-xs sm:text-sm text-theme-muted leading-relaxed font-light zen-sans">
                    {cleanExcerpt(post.contentMd, 150)}...
                  </p>
                </div>

                <div className="shrink-0 pt-2 sm:pt-0">
                  <Link href={`/blog/${post.slug}`} className="text-xs font-bold uppercase tracking-wider text-theme-text hover:text-emerald-500 transition-colors zen-sans inline-flex items-center gap-1">
                    <span>Ler</span>
                    <span>→</span>
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* WIDGETS INFERIORES ZEN */}
        <div className="pt-16 grid grid-cols-1 md:grid-cols-2 gap-8 zen-sans">
          <div className="bg-theme-surface rounded-2xl p-8 border border-theme-border/60 shadow-lg space-y-4">
            <h3 className="font-bold text-sm text-theme-text uppercase tracking-wider">✉️ Boletim Contemplativo</h3>
            <p className="text-xs text-theme-muted leading-relaxed">Receba nossas leituras e reflexões selecionadas pela IA semanalmente.</p>
            <NewsletterWidget blogId={String(blog.id)} />
          </div>

          <div className="bg-theme-surface rounded-2xl p-8 border border-theme-border/60 shadow-lg space-y-4">
            <h3 className="font-bold text-sm text-theme-text uppercase tracking-wider">⏱️ Histórico de Leitura</h3>
            <ReadingHistory />
          </div>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
