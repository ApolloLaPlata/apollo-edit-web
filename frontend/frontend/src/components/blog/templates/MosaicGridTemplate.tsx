// ────────────────────────────────────────────────────────────
// Template 3: MOSAIC GRID (Tech, Games & Fotografia Premium)
// Nicho: Tecnologia, games, esportes, lifestyle, fotografia
// Fontes: Space Grotesk (títulos) + Outfit (corpo)
// Layout: Hero Duplo Assimétrico + Mosaico Cyber/Tech de Alta Precisão
// Design Refatorado: Cyberpunk Elegante, Neon Borders, Glassmorphism e Dinamismo
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

export default function MosaicGridTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#10b981';
  const secondary = blog.secondaryColor || '#f97316';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  // Distribuição do mosaico
  const featuredA = allPosts[0] || null;   // grande (esq)
  const featuredB = allPosts[1] || null;   // médio (dir topo)
  const featuredC = allPosts[2] || null;   // médio (dir baixo)
  const gridPosts = allPosts.slice(3);     // cards restantes

  return (
    <main className="min-h-screen bg-theme-bg text-theme-text transition-colors duration-500" style={{ fontFamily: "'Outfit', sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800;900&family=Outfit:wght@400;500;600;700;800&display=swap');
        .tech-grotesk { font-family: 'Space Grotesk', sans-serif; }
        .tech-border { border-image: linear-gradient(to right, ${primary}, ${secondary}) 1; }
      `}</style>

      {/* ── TOPBAR TECH ── */}
      <div className="w-full py-2 px-4 text-center text-xs font-black uppercase tracking-widest text-white shadow-lg flex items-center justify-center gap-2" style={{ background: `linear-gradient(90deg, #064e3b, ${primary}, #064e3b)` }}>
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
        <span>⚡ TECH MOSAICO • HARDWARE, GAMES & IA MONITORADOS 24/7</span>
      </div>

      {/* ── NAVBAR PREMIUM GLASSMORPHISM ── */}
      <NavbarMaster blog={blog} categories={categories} lang={lang} domain={domain} />

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── WEB STORIES VIRAL FEED ── */}
      <div className="pt-2 max-w-7xl mx-auto">
        <WebStories posts={allPosts} domain={domain} />
      </div>

      {/* ── HERO DUPLO ASSIMÉTRICO CYBER/TECH (MOSAICO TOPO) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 pb-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-auto lg:h-[520px]">
          
          {/* Card A — grande (2/3) */}
          {featuredA && (
            <article className="lg:col-span-2 relative rounded-3xl overflow-hidden group shadow-2xl h-80 lg:h-auto border border-theme-border/80 hover:border-emerald-500/60 transition-all duration-500 flex flex-col justify-end">
              <Link href={`/blog/${featuredA.slug}`} className="absolute inset-0 z-0 bg-slate-950">
                {featuredA.coverImage ? (
                  <img src={featuredA.coverImage} alt={featuredA.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-[2000ms] ease-out" loading="eager" fetchPriority="high" />
                ) : (
                  <div className="w-full h-full" style={{ background: `linear-gradient(135deg, #0f172a, ${primary}50)` }} />
                )}
              </Link>
              <div className="absolute inset-0 z-10 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent opacity-90 group-hover:opacity-80 transition-opacity" />
              
              <div className="absolute top-6 left-6 z-20 flex items-center gap-2">
                <span className="px-3.5 py-1 rounded-full text-[10px] font-black uppercase tracking-widest text-white shadow-lg backdrop-blur-md" style={{ backgroundColor: primary }}>
                  🔥 Top Tech Review
                </span>
                {featuredA.category && (
                  <span className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-black/70 text-slate-200 backdrop-blur-md border border-white/10">
                    {featuredA.category}
                  </span>
                )}
              </div>

              <div className="p-8 relative z-20 space-y-3">
                <div className="text-xs text-slate-300 font-mono font-bold">
                  ✍️ {featuredA.author} • 📅 {fmtDate(featuredA.createdAt)}
                </div>
                <Link href={`/blog/${featuredA.slug}`}>
                  <h1 className="text-2xl sm:text-4xl font-black text-white leading-tight tech-grotesk group-hover:text-emerald-400 transition-colors">
                    {featuredA.title}
                  </h1>
                </Link>
                <p className="text-slate-300 text-sm line-clamp-2 hidden sm:block font-normal">
                  {cleanExcerpt(featuredA.contentMd, 200)}...
                </p>
              </div>
            </article>
          )}

          {/* Cards B e C — coluna direita */}
          <div className="flex flex-col gap-6 h-full">
            {[featuredB, featuredC].map((post, i) => post && (
              <article key={post.id} className="relative flex-1 rounded-3xl overflow-hidden group shadow-xl h-56 lg:h-auto border border-theme-border/80 hover:border-emerald-500/60 transition-all duration-500 flex flex-col justify-end">
                <Link href={`/blog/${post.slug}`} className="absolute inset-0 z-0 bg-slate-950">
                  {post.coverImage ? (
                    <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out" loading="lazy" />
                  ) : (
                    <div className="w-full h-full" style={{ background: `linear-gradient(135deg, #0f172a, ${secondary}50)` }} />
                  )}
                </Link>
                <div className="absolute inset-0 z-10 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent opacity-90 group-hover:opacity-80 transition-opacity" />
                
                <div className="absolute top-4 left-4 z-20">
                  <span className="px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-wider bg-black/80 text-white backdrop-blur-md border border-white/10">
                    {post.category || (i === 0 ? '⚡ Trending' : '🎮 Spotlight')}
                  </span>
                </div>

                <div className="p-6 relative z-20 space-y-1.5">
                  <div className="text-[10px] text-slate-400 font-mono font-bold">
                    📅 {fmtDate(post.createdAt)} • ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min
                  </div>
                  <Link href={`/blog/${post.slug}`}>
                    <h2 className="text-base sm:text-lg font-black text-white leading-snug tech-grotesk group-hover:text-emerald-400 transition-colors line-clamp-2">
                      {post.title}
                    </h2>
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>

      {/* ── CONTEÚDO PRINCIPAL (12 COLUNAS) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">

          {/* COLUNA PRINCIPAL: MOSAICO DE CARDS (8 col) */}
          <div className="lg:col-span-8 space-y-8">
            <div className="flex items-center justify-between border-b border-theme-border/80 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-2 h-8 rounded-full shadow-sm" style={{ backgroundColor: primary }} />
                <div>
                  <h2 className="text-xl sm:text-2xl font-black text-theme-text uppercase tracking-tight tech-grotesk">
                    Mosaico de Hardware & Análises
                  </h2>
                  <p className="text-xs text-theme-muted font-medium">Relatórios técnicos, setups e reviews de precisão</p>
                </div>
              </div>
              <span className="text-xs font-mono font-bold text-theme-muted bg-theme-surface px-3 py-1.5 rounded-lg border border-theme-border">
                {gridPosts.length} Artigos
              </span>
            </div>

            <div className="w-full">
              <AdBanner type="horizontal" domain={domain} />
            </div>

            {/* GRADE MOSAICO (2 COLUNAS) */}
            {gridPosts.length === 0 ? (
              <div className="py-16 text-center bg-theme-surface/50 rounded-3xl border border-dashed border-theme-border p-8">
                <span className="text-4xl block mb-3">🎮</span>
                <h3 className="font-bold text-base text-theme-text">Nenhuma outra análise no momento</h3>
                <p className="text-xs text-theme-muted mt-1">O enxame tech está redigindo novos relatórios para este mosaico.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {gridPosts.map((post) => (
                  <article
                    key={post.id}
                    className="group bg-theme-surface/90 backdrop-blur-md rounded-2xl overflow-hidden border border-theme-border shadow-md hover:shadow-2xl hover:border-emerald-500/60 hover:-translate-y-1.5 transition-all duration-300 flex flex-col justify-between"
                  >
                    <div>
                      {/* Imagem */}
                      <Link href={`/blog/${post.slug}`} className="block relative h-48 w-full overflow-hidden bg-slate-900">
                        {post.coverImage ? (
                          <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" loading="lazy" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #1e293b, ${primary}30)` }}>
                            <span className="text-3xl opacity-30">💻</span>
                          </div>
                        )}
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
                        
                        {post.category && (
                          <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider bg-black/70 text-white backdrop-blur-md border border-white/10">
                            {post.category}
                          </span>
                        )}
                      </Link>

                      {/* Conteúdo */}
                      <div className="p-5 space-y-2.5">
                        <div className="flex items-center justify-between text-[10px] text-theme-muted font-mono font-bold">
                          <span>📅 {fmtDate(post.createdAt)}</span>
                          <span>⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                        </div>

                        <Link href={`/blog/${post.slug}`}>
                          <h3 className="font-extrabold text-base text-theme-text leading-snug line-clamp-2 tech-grotesk group-hover:text-emerald-400 transition-colors">
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
                      <Link href={`/blog/${post.slug}`} className="text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                        <span>Ler Review</span>
                        <span>→</span>
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>

          {/* COLUNA DA DIREITA: SIDEBAR (4 col) */}
          <aside className="lg:col-span-4 space-y-8 sticky top-24">
            
            {/* WIDGET 1: SOBRE O MOSAICO */}
            <div className="bg-theme-surface rounded-3xl p-6 border border-theme-border shadow-xl space-y-4 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-bl from-emerald-500/10 via-green-500/5 to-transparent rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl shadow-md" style={{ background: `linear-gradient(135deg, ${primary}, ${secondary})` }}>
                  💻
                </div>
                <div>
                  <h3 className="font-extrabold text-base text-theme-text uppercase tracking-tight tech-grotesk">Laboratório Tech IA</h3>
                  <p className="text-xs text-theme-muted font-mono">Monitoramento 24/7</p>
                </div>
              </div>
              <p className="text-xs text-theme-muted leading-relaxed font-normal">
                {blog.description || `O ${blog.name} analisa benchmarks, hardware de ponta e desenvolvimentos Tecnológicos de forma 100% independente.`}
              </p>
              <div className="pt-2 border-t border-theme-border/60 flex items-center justify-between text-[11px] font-bold font-mono text-theme-muted">
                <span>Core: <strong className="text-emerald-400">● 100% Ativo</strong></span>
                <span>Reviews: <strong className="text-theme-text">{allPosts.length}+</strong></span>
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
              <h3 className="font-extrabold text-sm text-theme-text uppercase tracking-wider pb-2 border-b border-theme-border tech-grotesk">
                📂 Setores de Tecnologia
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
