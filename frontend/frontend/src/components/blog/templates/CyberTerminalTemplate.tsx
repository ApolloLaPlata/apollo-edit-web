// ────────────────────────────────────────────────────────────
// Template 8: CYBER TERMINAL (Hacker, IA, Cripto & Programação Premium)
// Nicho: Criptomoedas, Inteligência Artificial, programação, hacking, cybersec, tech
// Fontes: Fira Code (terminal mono) + Inter (metadados)
// Layout: Estilo Terminal Hacker Matrix / Vercel CLI / Linux Root
// Design Refatorado: Cyberpunk Neon, Glowing Borders, Terminal Logs & Alta Precisão
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

export default function CyberTerminalTemplate({ blog, heroPost, otherPosts, categories, lang, domain }: TemplateProps) {
  const primary = blog.primaryColor || '#10b981';
  const secondary = blog.secondaryColor || '#06b6d4';
  const allPosts = heroPost ? [heroPost, ...otherPosts] : otherPosts;

  return (
    <main className="min-h-screen bg-[#050908] text-[#10b981] transition-colors duration-500 font-mono">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
        .cyber-mono { font-family: 'Fira Code', monospace; }
        .cyber-glow { box-shadow: 0 0 35px rgba(16, 185, 129, 0.25); }
        .cyber-border { border: 1px solid rgba(16, 185, 129, 0.4); }
      `}</style>

      {/* ── TOPBAR CYBER TERMINAL ── */}
      <div className="w-full py-1.5 px-4 bg-black border-b border-emerald-500/30 text-[11px] font-bold text-emerald-400 cyber-mono flex justify-between items-center gap-4 overflow-x-auto no-scrollbar">
        <div className="flex items-center gap-3 shrink-0">
          <span className="flex items-center gap-1.5 text-emerald-400 font-extrabold animate-pulse">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            root@colmeia:~#
          </span>
          <span className="text-slate-400">[SYSTEM_OK]</span>
          <span className="text-slate-400">DAEMON_AI: <strong className="text-emerald-400">ONLINE 24/7</strong></span>
        </div>
        <div className="shrink-0 text-slate-500 text-[10px]">
          EXEC_MODE: AUTONOMOUS_PUBLISHING_V2.4
        </div>
      </div>

      {/* ── NAVBAR HACKER MATRIX ── */}
      <nav className="w-full bg-[#050908]/95 backdrop-blur-md border-b border-emerald-500/40 sticky top-0 z-50 cyber-glow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex justify-between items-center gap-6">
          
          <Link href={`/?lang=${lang}`} className="flex items-center gap-3 shrink-0 group">
            {blog.logoUrl ? (
              <img src={blog.logoUrl} alt={blog.name} className="h-8 max-w-[150px] object-contain group-hover:scale-105 transition-transform" />
            ) : (
              <div className="w-9 h-9 rounded bg-black border border-emerald-500 flex items-center justify-center font-bold text-emerald-400 text-sm shadow-[0_0_15px_rgba(16,185,129,0.5)] group-hover:scale-105 transition-transform">
                &gt;_
              </div>
            )}
            <div className="flex flex-col">
              <span className="font-bold text-xl tracking-tight text-white uppercase cyber-mono group-hover:text-emerald-400 transition-colors">
                {blog.name}
              </span>
              <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-emerald-600 -mt-1">
                {blog.niche || 'Cyber & Cripto'}
              </span>
            </div>
          </Link>

          <div className="hidden lg:flex gap-6 items-center">
            {categories.slice(0, 6).map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="text-xs font-bold uppercase tracking-widest text-slate-400 hover:text-emerald-400 transition-colors">
                /{cat.name}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <SearchBar domain={domain} lang={lang} />
            <Link href="/admin" className="hidden sm:inline-flex items-center gap-1.5 text-[10px] uppercase font-bold bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-400 px-3 py-1.5 rounded border border-emerald-500/40 transition">
              <span>&gt;</span> sudo admin
            </Link>
          </div>
        </div>
      </nav>

      <NewsTicker posts={allPosts} domain={domain} />

      {/* ── TERMINAL HERO (MANCHETE DE SISTEMA) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-10">
        {heroPost && (
          <article className="group relative bg-black/80 rounded-2xl overflow-hidden border border-emerald-500/50 cyber-glow p-6 md:p-10 space-y-6">
            <div className="flex flex-col md:flex-row gap-8 items-center">
              
              <Link href={`/blog/${heroPost.slug}`} className="w-full md:w-1/2 h-64 md:h-80 rounded-xl overflow-hidden border border-emerald-500/30 bg-slate-950 shrink-0 relative group">
                {heroPost.coverImage ? (
                  <img src={heroPost.coverImage} alt={heroPost.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out opacity-85" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-black"><span className="text-6xl">💻</span></div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-60" />
                <div className="absolute top-3 left-3 bg-black/80 px-2.5 py-1 rounded text-[10px] font-bold text-emerald-400 border border-emerald-500/40">
                  [LOG_ID: #001_MAIN]
                </div>
              </Link>

              <div className="flex-1 space-y-4">
                <div className="flex items-center gap-3 text-xs text-emerald-600 font-bold">
                  <span>&gt; EXEC_TIME: {fmtDate(heroPost.createdAt)}</span>
                  <span>•</span>
                  <span>AUTHOR: <strong className="text-emerald-400">{heroPost.author}</strong></span>
                </div>

                <Link href={`/blog/${heroPost.slug}`}>
                  <h1 className="text-2xl sm:text-4xl font-bold text-white leading-tight group-hover:text-emerald-400 transition-colors">
                    {heroPost.title}
                  </h1>
                </Link>

                <div className="p-4 bg-emerald-950/20 rounded border border-emerald-500/20 text-slate-300 text-xs sm:text-sm leading-relaxed font-normal">
                  <span className="text-emerald-500 font-bold">&gt; SUMMARY: </span>
                  {cleanExcerpt(heroPost.contentMd, 240)}...
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <Link
                    href={`/blog/${heroPost.slug}`}
                    className="inline-flex items-center gap-2 px-6 py-3 rounded font-bold text-xs uppercase tracking-wider text-black bg-emerald-400 hover:bg-emerald-300 shadow-[0_0_20px_rgba(16,185,129,0.8)] transition-all hover:scale-105 active:scale-95"
                  >
                    <span>&gt; DECRYPT_AND_READ()</span>
                    <span>→</span>
                  </Link>
                  <span className="text-xs font-bold text-slate-500">
                    ⏱️ ~{Math.max(2, Math.ceil(heroPost.contentMd.length / 800))} min
                  </span>
                </div>
              </div>

            </div>
          </article>
        )}
      </div>

      {/* ANÚNCIO INTERMEDIÁRIO */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <AdBanner type="horizontal" domain={domain} />
      </div>

      {/* ── FEED LOG DE SISTEMA (2 COLUNAS) ── */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20 space-y-8">
        <div className="flex items-center justify-between border-b border-emerald-500/30 pb-4">
          <div className="flex items-center gap-2 text-white font-bold text-lg">
            <span className="text-emerald-500">&gt;</span>
            <span>SYSTEM_LOGS // RECENT_TRANSACTIONS</span>
          </div>
          <span className="text-xs font-bold text-emerald-500 bg-emerald-950/40 px-3 py-1 rounded border border-emerald-500/30">
            {otherPosts.length} NODES
          </span>
        </div>

        {otherPosts.length === 0 ? (
          <div className="py-16 text-center bg-black/60 rounded-xl border border-dashed border-emerald-500/40 p-8">
            <span className="text-4xl block mb-3">💻</span>
            <h3 className="font-bold text-base text-white">Nenhum log registrado no momento</h3>
            <p className="text-xs text-slate-400 mt-1">O enxame cyber está compilando novos relatórios para este terminal.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {otherPosts.map((post, idx) => (
              <article
                key={post.id}
                className="group bg-black/80 rounded-xl overflow-hidden border border-emerald-500/30 hover:border-emerald-500 hover:shadow-[0_0_25px_rgba(16,185,129,0.2)] transition-all duration-300 flex flex-col justify-between"
              >
                <div>
                  <Link href={`/blog/${post.slug}`} className="block relative h-48 w-full overflow-hidden bg-slate-950">
                    {post.coverImage ? (
                      <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out opacity-80" loading="lazy" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-black"><span className="text-3xl opacity-30">⚡</span></div>
                    )}
                    <div className="absolute top-2 left-2 bg-black/90 px-2 py-0.5 rounded text-[9px] font-bold text-emerald-400 border border-emerald-500/40">
                      NODE_#{idx + 1}: {post.category || 'CYBER'}
                    </div>
                  </Link>

                  <div className="p-5 space-y-2">
                    <div className="flex items-center justify-between text-[10px] text-emerald-600 font-bold">
                      <span>TIMESTAMP: {fmtDate(post.createdAt)}</span>
                      <span>⏱️ {Math.max(1, Math.ceil(post.contentMd.length / 800))}m</span>
                    </div>

                    <Link href={`/blog/${post.slug}`}>
                      <h3 className="font-bold text-base text-white leading-snug line-clamp-2 group-hover:text-emerald-400 transition-colors">
                        {post.title}
                      </h3>
                    </Link>

                    <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed font-normal">
                      {cleanExcerpt(post.contentMd, 120)}...
                    </p>
                  </div>
                </div>

                <div className="px-5 py-3 bg-emerald-950/20 border-t border-emerald-500/20 flex items-center justify-between text-[11px] font-bold">
                  <span className="text-slate-500 truncate max-w-[140px]">USR: {(post.author || '').replace(/Redação IA/gi, (post as any).blog_name || 'Equipe Especial') || (post as any).blog_name || 'Redação'}</span>
                  <Link href={`/blog/${post.slug}`} className="text-emerald-400 group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                    <span>&gt; READ_FILE()</span>
                    <span>→</span>
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* WIDGETS INFERIORES */}
        <div className="pt-12 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-black/80 rounded-xl p-8 border border-emerald-500/30 cyber-glow space-y-4">
            <h3 className="font-bold text-base text-white uppercase tracking-wider">&gt; SUBSCRIB_DAEMON --newsletter</h3>
            <p className="text-xs text-slate-400 leading-relaxed">Receba alertas de vulnerabilidades, análises de especialistas e relatórios cripto em tempo real.</p>
            <NewsletterWidget blogId={String(blog.id)} />
          </div>

          <div className="bg-black/80 rounded-xl p-8 border border-emerald-500/30 cyber-glow space-y-4">
            <h3 className="font-bold text-base text-white uppercase tracking-wider">&gt; SYSTEM_HISTORY --logs</h3>
            <ReadingHistory />
          </div>
        </div>
      </div>

      <Footer blogName={blog.name} domain={domain} />
    </main>
  );
}
