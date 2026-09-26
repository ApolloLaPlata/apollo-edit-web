// ────────────────────────────────────────────────────────────
// Template 4: EDITORIAL PROSE (Literatura, Prosa & Viagens Premium)
// Nicho: Literatura, ensaios, viagens, história, filosofia, cultura
// Fontes: Merriweather (títulos e corpo literário) + Inter (metadados)
// Layout: Coluna Única Centralizada de Alto Respiro + Sem Sidebar + Foco Literário
// Design Refatorado: The Atlantic / Medium Premium, Leitura Confortável e Elegância
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

export default function EditorialProseTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#d97706';
  const secondary = blog.secondaryColor || '#b45309';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500" style={{ fontFamily: "'Merriweather', serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Merriweather:ital,wght@0,300;0,400;0,700;0,900;1,300;1,400&family=Inter:wght@400;500;600;700;800&display=swap');
        .prose-sans { font-family: 'Inter', sans-serif; }
      `}</style>

      {/* ── TOPBAR LITERÁRIA ── */}
      <div className="w-full py-2 px-4 text-center text-[11px] font-bold uppercase tracking-[0.25em] text-white shadow-sm prose-sans" style={{ background: `linear-gradient(90deg, #451a03, ${primary}, #451a03)` }}>
        <span>📖 EDIÇÃO LITERÁRIA EM PROSA • ENSAIOS & CRÔNICAS CURADAS PELA REDAÇÃO</span>
      </div>

      {/* ── NAVBAR LITERÁRIA MINIMALISTA ── */}
      <nav className="w-full bg-theme-surface/95 backdrop-blur-md border-b border-theme-border sticky top-0 z-50 shadow-md prose-sans">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-4 flex justify-between items-center gap-6">
          
          <Link href={`/?lang=${lang}`} className="flex items-center gap-3 shrink-0 group">
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-8 max-w-[150px] object-contain group-hover:scale-105 transition-transform" />
            ) : (
              <div className="w-9 h-9 rounded-full flex items-center justify-center font-bold text-white text-base shadow-md group-hover:scale-105 transition-transform" style={{ backgroundColor: primary }}>
                {blog.name?.charAt(0) || 'E'}
              </div>
            )}
            <div className="flex flex-col">
              <span className="font-black text-xl tracking-tight text-theme-text uppercase font-serif group-hover:opacity-90 transition-opacity">
                {blog.name}
              </span>
              <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-theme-muted -mt-1">
                {blog.niche || 'Ensaios & Crônicas'}
              </span>
            </div>
          </Link>

          <div className="hidden md:flex gap-6 items-center">
            {categories.slice(0, 5).map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="text-xs font-bold uppercase tracking-widest text-theme-muted hover:text-theme-text transition-colors">
                {cat.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <SearchBar domain={domain} lang={lang} />
            <Link href="/admin" className="hidden sm:inline-flex items-center gap-1 text-[10px] uppercase font-bold bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg transition">
              Admin
            </Link>
          </div>
        </div>
      </nav>

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── ENSAIO PRINCIPAL (HERO CENTRALIZADO DE ALTO RESPIRO) ── */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 md:py-20 text-center space-y-8">
        {heroPost && (
          <article className="space-y-6">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs font-bold uppercase tracking-widest prose-sans">
              <span>★ Ensaio Em Destaque</span>
              {heroPost.category && <span>• {heroPost.category}</span>}
            </div>

            <Link href={`/blog/${heroPost.slug}`}>
              <h1 className="text-3xl sm:text-5xl md:text-6xl font-black leading-[1.15] text-theme-text hover:text-amber-500 transition-colors tracking-tight">
                {heroPost.title}
              </h1>
            </Link>

            <div className="flex justify-center items-center gap-3 text-xs text-theme-muted font-bold uppercase tracking-wider prose-sans">
              <span>Por <strong className="text-theme-text">{heroPost.author}</strong></span>
              <span>•</span>
              <span>{fmtDate(heroPost.createdAt)}</span>
              <span>•</span>
              <span>~{Math.max(3, Math.ceil(heroPost.contentMd.length / 800))} min de leitura</span>
            </div>

            {heroPost.coverImage && (
              <Link href={`/blog/${heroPost.slug}`} className="block my-8 rounded-3xl overflow-hidden shadow-2xl border border-theme-border/60 max-h-[480px] group">
                <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out" />
              </Link>
            )}

            <p className="text-lg sm:text-xl text-theme-muted leading-relaxed font-light italic max-w-3xl mx-auto">
              "{cleanExcerpt(heroPost.contentMd, 320)}..."
            </p>

            <div className="pt-6">
              <Link
                href={`/blog/${heroPost.slug}`}
                className="inline-flex items-center gap-3 px-8 py-4 rounded-full font-bold text-xs uppercase tracking-widest text-white shadow-xl transition-all hover:scale-105 active:scale-95 prose-sans"
                style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
              >
                <span>Ler Ensaio Completo</span>
                <span>→</span>
              </Link>
            </div>
          </article>
        )}
      </div>

      {/* ANÚNCIO INTERMEDIÁRIO */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 pb-12">
        <AdBanner type="horizontal" domain={domain} />
      </div>

      {/* ── LISTA DE CRÔNICAS & ENSAIOS (ESTILO MEDIUM / NEW YORKER) ── */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 pb-20 space-y-12">
        <div className="border-b border-theme-border/80 pb-4 text-center prose-sans">
          <h2 className="text-xl font-black uppercase tracking-widest text-theme-text">
            Outras Crônicas & Publicações
          </h2>
          <p className="text-xs text-theme-muted mt-1">Acervo literário redigido continuamente pela Equipe de Jornalistas</p>
        </div>

        {otherPosts.length === 0 ? (
          <div className="py-16 text-center bg-theme-surface/30 rounded-3xl border border-dashed border-theme-border p-8 prose-sans">
            <span className="text-4xl block mb-3">📜</span>
            <h3 className="font-bold text-base text-theme-text">Nenhuma outra crônica no momento</h3>
            <p className="text-xs text-theme-muted mt-1">O enxame literário está redigindo novos ensaios para esta edição.</p>
          </div>
        ) : (
          <div className="divide-y divide-theme-border/60 space-y-10">
            {otherPosts.map((post) => (
              <article key={post.id} className="pt-10 first:pt-0 group grid grid-cols-1 md:grid-cols-12 gap-8 items-center">
                
                {/* Conteúdo Literário (8 col) */}
                <div className="md:col-span-8 space-y-3">
                  <div className="flex items-center gap-2 text-xs text-amber-500 font-bold uppercase tracking-widest prose-sans">
                    <span>{post.category || 'Ensaio'}</span>
                    <span>•</span>
                    <span className="text-theme-muted">{fmtDate(post.createdAt)}</span>
                  </div>

                  <Link href={`/blog/${post.slug}`}>
                    <h3 className="text-2xl sm:text-3xl font-bold text-theme-text leading-snug group-hover:text-amber-500 transition-colors">
                      {post.title}
                    </h3>
                  </Link>

                  <p className="text-sm sm:text-base text-theme-muted leading-relaxed font-normal">
                    {cleanExcerpt(post.contentMd, 180)}...
                  </p>

                  <div className="pt-2 flex items-center justify-between text-xs font-bold text-theme-muted prose-sans">
                    <span>Por <strong className="text-theme-text">{(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</strong></span>
                    <Link href={`/blog/${post.slug}`} className="text-amber-500 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                      <span>Continuar Lendo</span>
                      <span>→</span>
                    </Link>
                  </div>
                </div>

                {/* Foto Capa Lateral (4 col) */}
                {post.coverImage && (
                  <Link href={`/blog/${post.slug}`} className="md:col-span-4 h-48 rounded-2xl overflow-hidden shadow-lg border border-theme-border/40 block">
                    <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" loading="lazy" />
                  </Link>
                )}
              </article>
            ))}
          </div>
        )}

        {/* WIDGETS INFERIORES LITERÁRIOS */}
        <div className="pt-16 grid grid-cols-1 md:grid-cols-2 gap-8 prose-sans">
          <div className="bg-theme-surface rounded-3xl p-8 border border-theme-border shadow-xl space-y-4">
            <h3 className="font-extrabold text-base text-theme-text uppercase tracking-wider">✉️ Assine o Boletim Literário</h3>
            <p className="text-xs text-theme-muted leading-relaxed">Receba nossos ensaios e crônicas curadas pela IA diretamente no seu e-mail.</p>
            <NewsletterWidget blogId={String(blog.id)} />
          </div>

          <div className="bg-theme-surface rounded-3xl p-8 border border-theme-border shadow-xl space-y-4">
            <h3 className="font-extrabold text-base text-theme-text uppercase tracking-wider">⏱️ Histórico de Leitura</h3>
            <ReadingHistory />
          </div>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
