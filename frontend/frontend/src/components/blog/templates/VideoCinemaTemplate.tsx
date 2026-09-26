// ────────────────────────────────────────────────────────────
// Template 6: VIDEO CINEMA (Vídeo, Trailers & Streaming 4K Premium)
// Nicho: Cinema, vídeos, trailers, streaming, entretenimento audiovisual
// Fontes: Outfit (títulos e corpo moderno)
// Layout: Hero Imersivo Widescreen 16:9 + Grid Estilo Netflix/YouTube + Dark Mode Cinema
// Design Refatorado: Cinema 4K, Glow Vermelho/Alaranjado, Glassmorphism e Foco Visual
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

export default function VideoCinemaTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#ef4444';
  const secondary = blog.secondaryColor || '#f97316';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-[#050508] text-white transition-colors duration-500" style={{ fontFamily: "'Outfit', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');
        .cinema-glow { box-shadow: 0 0 50px rgba(239, 68, 68, 0.25); }
      `}</style>

      {/* ── TOPBAR CINEMATOGRÁFICA ── */}
      <div className="w-full py-2 px-4 text-center text-xs font-black uppercase tracking-[0.25em] text-white shadow-lg flex items-center justify-center gap-2" style={{ background: `linear-gradient(90deg, #450a0a, ${primary}, #450a0a)` }}>
        <span className="w-2 h-2 rounded-full bg-red-400 animate-ping" />
        <span>🎬 CINEMA & STREAMING 4K • PRODUÇÃO AUDIOVISUAL POR EQUIPE AUDIOVISUAL</span>
      </div>

      {/* ── NAVBAR CINEMA PREMIADA ── */}
      <nav className="w-full bg-[#0a0a0f]/90 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center gap-6">
          
          <Link href={`/?lang=${lang}`} className="flex items-center gap-3.5 shrink-0 group">
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-9 max-w-[160px] object-contain group-hover:scale-105 transition-transform" />
            ) : (
              <div className="w-10 h-10 rounded-xl flex items-center justify-center font-black text-white text-lg shadow-lg group-hover:scale-110 transition-transform" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                {blog.name?.charAt(0) || 'C'}
              </div>
            )}
            <div className="flex flex-col">
              <span className="font-black text-2xl tracking-tight text-white uppercase group-hover:text-red-500 transition-colors">
                {blog.name}
              </span>
              <span className="text-[9px] font-extrabold uppercase tracking-[0.25em] text-slate-400 font-mono -mt-1">
                {blog.niche || 'Áudio & Vídeo'}
              </span>
            </div>
          </Link>

          <div className="hidden lg:flex gap-7 items-center">
            {categories.slice(0, 6).map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="text-xs font-extrabold uppercase tracking-widest text-slate-300 hover:text-white hover:scale-105 transition-all">
                {cat.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex gap-1 bg-white/5 p-1 rounded-xl border border-white/10">
              <Link href={`/?lang=pt`} className={`px-2 py-1 rounded-lg text-sm transition-all ${lang === 'pt' ? 'bg-red-600 font-bold' : 'opacity-40 hover:opacity-100'}`} title="Português">🇧🇷</Link>
              <Link href={`/?lang=en`} className={`px-2 py-1 rounded-lg text-sm transition-all ${lang === 'en' ? 'bg-red-600 font-bold' : 'opacity-40 hover:opacity-100'}`} title="English">🇺🇸</Link>
              <Link href={`/?lang=es`} className={`px-2 py-1 rounded-lg text-sm transition-all ${lang === 'es' ? 'bg-red-600 font-bold' : 'opacity-40 hover:opacity-100'}`} title="Español">🇪🇸</Link>
            </div>
            
            <SearchBar domain={domain} lang={lang} />
            
            <Link href="/admin" className="hidden sm:inline-flex items-center gap-1.5 text-[11px] uppercase font-extrabold bg-white/10 hover:bg-white/20 text-white px-3.5 py-2 rounded-xl border border-white/10 transition-all hover:scale-105">
              <span>⚡</span> Admin
            </Link>
          </div>
        </div>
      </nav>

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── HERO IMERSIVO WIDESCREEN 16:9 (ESTILO NETFLIX / YOUTUBE PRO) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12">
        {heroPost && (
          <article className="group relative rounded-3xl overflow-hidden shadow-2xl border border-white/10 cinema-glow">
            <Link href={`/blog/${heroPost.slug}`} className="relative block h-[420px] sm:h-[540px] w-full overflow-hidden bg-black">
              {heroPost.coverImage ? (
                <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[2000ms] ease-out opacity-80" loading="eager" fetchPriority="high" />
              ) : (
                <div className="w-full h-full flex items-center justify-center" style={{ background: `radial-gradient(circle at center, ${primary}40 0%, #050508 80%)` }}>
                  <span className="text-8xl opacity-30">🎬</span>
                </div>
              )}
              {/* Gradiente de proteção */}
              <div className="absolute inset-0 bg-gradient-to-t from-[#050508] via-[#050508]/50 to-transparent opacity-90 group-hover:opacity-80 transition-opacity" />
              
              {/* Ícone de Play Central */}
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-red-600/90 text-white flex items-center justify-center text-3xl shadow-[0_0_40px_rgba(239,68,68,0.8)] group-hover:scale-110 transition-transform">
                  ▶
                </div>
              </div>

              {/* Badges superiores */}
              <div className="absolute top-6 left-6 z-20 flex items-center gap-2.5">
                <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest text-white shadow-lg backdrop-blur-md" style={{ backgroundColor: primary }}>
                  🔥 Trailer & Review Oficial
                </span>
                {heroPost.category && (
                  <span className="px-3.5 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-black/70 text-slate-200 backdrop-blur-md border border-white/10">
                    {heroPost.category}
                  </span>
                )}
              </div>
            </Link>

            {/* Conteúdo sobreposto na parte inferior */}
            <div className="p-8 sm:p-12 -mt-24 relative z-20 space-y-4">
              <div className="flex items-center gap-3 text-xs text-slate-300 font-mono font-bold">
                <span>✍️ Por <strong className="text-white">{heroPost.author}</strong></span>
                <span>•</span>
                <span>📅 {fmtDate(heroPost.createdAt)}</span>
                <span>•</span>
                <span className="text-red-400 font-extrabold">4K ULTRA HD</span>
              </div>

              <Link href={`/blog/${heroPost.slug}`}>
                <h1 className="text-3xl sm:text-5xl font-black text-white leading-tight group-hover:text-red-500 transition-colors tracking-tight">
                  {heroPost.title}
                </h1>
              </Link>

              <p className="text-slate-300 text-sm sm:text-base leading-relaxed line-clamp-2 max-w-3xl font-normal">
                {cleanExcerpt(heroPost.contentMd, 260)}...
              </p>

              <div className="pt-4 flex items-center gap-4 flex-wrap">
                <Link
                  href={`/blog/${heroPost.slug}`}
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-black text-xs uppercase tracking-widest text-white shadow-2xl transition-all hover:scale-105 active:scale-95"
                  style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}
                >
                  <span>▶ Assistir / Ler Crítica</span>
                  <span>→</span>
                </Link>
                <span className="text-xs font-bold text-slate-400 font-mono">
                  ⏱️ ~{Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} min de leitura
                </span>
              </div>
            </div>
          </article>
        )}
      </div>

      {/* ANÚNCIO INTERMEDIÁRIO */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-10">
        <AdBanner type="horizontal" domain={domain} />
      </div>

      {/* ── GRADE ESTILO NETFLIX / YOUTUBE PRO (3 COLUNAS) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 space-y-8">
        <div className="flex items-center justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-8 rounded-full shadow-sm" style={{ backgroundColor: primary }} />
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-white uppercase tracking-tight">
                Em Alta • Vídeos & Análises
              </h2>
              <p className="text-xs text-slate-400 font-medium">Curadoria audiovisual redigida e monitorada pela Redação IA</p>
            </div>
          </div>
          <span className="text-xs font-mono font-bold text-slate-400 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10">
            {otherPosts.length} Publicações
          </span>
        </div>

        {otherPosts.length === 0 ? (
          <div className="py-16 text-center bg-white/5 rounded-3xl border border-dashed border-white/10 p-8">
            <span className="text-4xl block mb-3">🎥</span>
            <h3 className="font-bold text-base text-white">Nenhum outro vídeo no momento</h3>
            <p className="text-xs text-slate-400 mt-1">O enxame audiovisual está redigindo novas matérias para este portal.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {otherPosts.map((post) => (
              <article
                key={post.id}
                className="group bg-[#0f0f18] rounded-2xl overflow-hidden border border-white/10 shadow-xl hover:shadow-2xl hover:border-red-500/60 hover:-translate-y-1.5 transition-all duration-300 flex flex-col justify-between"
              >
                <div>
                  {/* Imagem Proporção Vídeo 16:9 */}
                  <Link href={`/blog/${post.slug}`} className="block relative h-48 w-full overflow-hidden bg-black">
                    {post.coverImage ? (
                      <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out opacity-85" loading="lazy" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #1e1e2f, ${primary}30)` }}>
                        <span className="text-3xl opacity-30">🎥</span>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0f0f18] via-transparent to-transparent opacity-80 group-hover:opacity-60 transition-opacity" />
                    
                    {/* Mini botão de play sobre o card */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="w-12 h-12 rounded-full bg-red-600 text-white flex items-center justify-center text-sm shadow-lg">▶</div>
                    </div>

                    {post.category && (
                      <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider bg-black/80 text-white backdrop-blur-md border border-white/10">
                        {post.category}
                      </span>
                    )}
                  </Link>

                  {/* Conteúdo */}
                  <div className="p-5 space-y-2.5">
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-bold">
                      <span>📅 {fmtDate(post.createdAt)}</span>
                      <span>⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                    </div>

                    <Link href={`/blog/${post.slug}`}>
                      <h3 className="font-black text-base text-white leading-snug line-clamp-2 group-hover:text-red-500 transition-colors">
                        {post.title}
                      </h3>
                    </Link>

                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed font-normal">
                      {cleanExcerpt(post.contentMd, 120)}...
                    </p>
                  </div>
                </div>

                {/* Rodapé do Card */}
                <div className="px-5 py-3.5 bg-black/40 border-t border-white/5 flex items-center justify-between text-[11px] font-extrabold">
                  <span className="text-slate-400 truncate max-w-[140px]">✍️ {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                  <Link href={`/blog/${post.slug}`} className="text-red-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                    <span>Assistir</span>
                    <span>→</span>
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* WIDGETS INFERIORES */}
        <div className="pt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-[#0f0f18] rounded-3xl p-8 border border-white/10 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-base text-white uppercase tracking-wider">✉️ Assine o Canal de Notícias</h3>
            <p className="text-xs text-slate-400 leading-relaxed">Receba trailers, críticas e lançamentos audiovisuais selecionados pela nossa Redação.</p>
            <NewsletterWidget blogId={String(blog.id)} />
          </div>

          <div className="bg-[#0f0f18] rounded-3xl p-8 border border-white/10 shadow-2xl space-y-4">
            <h3 className="font-extrabold text-base text-white uppercase tracking-wider">⏱️ Histórico de Leitura & Vídeo</h3>
            <ReadingHistory />
          </div>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
