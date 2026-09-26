import React from 'react';
import Link from 'next/link';
import db from '@/lib/db';

export default async function RelatedPosts({
  currentPostId,
  domain,
}: {
  currentPostId: string;
  domain: string;
}) {
  // Puxa 3 posts diferentes deste mesmo portal para reter o leitor
  const relatedRaw = await db
    .prepare(`
    SELECT Post.id, Post.title, Post.slug, Post.coverImage, Post.createdAt, Blog.name as blogName
    FROM Post
    JOIN Blog ON Post.blogId = Blog.id
    WHERE Blog.domain = ? AND Post.id != ?
    ORDER BY RANDOM()
    LIMIT 2
  `)
    .all(domain, currentPostId) as any[];

  // PONTO 41: Native Ad Injetado (Disfarçado de Notícia para fisgar CTR)
  const nativeAd = {
    id: 'native-ad-1',
    title: 'Pessoas com mais de 40 anos estão usando este truque estranho de 2 minutos...',
    slug: 'ofertas', // Aponta para a Rota de Escoamento de Tráfego
    coverImage: 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=600&q=80', // Imagem de pote médico genérico (Clickbait clássico)
    createdAt: new Date().toISOString(),
    blogName: 'Patrocinado',
    isAd: true
  };
  
  const related = [...relatedRaw];
  if (related.length > 0) {
    related.splice(1, 0, nativeAd); // Insere bem no meio dos posts reais (Posição 2)
  }


  if (related.length === 0) {
    return (
      <div className="mt-20">
        <div className="pt-10 border-t border-cyan-500/30 relative bg-gradient-to-b from-cyan-950/20 to-transparent p-8 rounded-3xl border border-cyan-500/20 text-center shadow-xl">
            <h3 className="text-xl font-black text-white mb-2 tracking-widest uppercase text-[12px]">✦ Novas Recomendações em Breve ✦</h3>
            <p className="text-slate-500 text-sm">Nossa equipe de redação está finalizando a apuração de novas matérias do portal.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-20 space-y-20">
      <div className="pt-10 border-t border-cyan-500/30 relative bg-gradient-to-b from-cyan-950/20 to-transparent p-8 rounded-3xl border border-cyan-500/20 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 relative z-10">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-[10px] font-black uppercase tracking-widest mb-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              Recomendações
            </div>
            <h3 className="text-xl md:text-2xl font-black text-white tracking-tight">
              Continue Lendo no {related[0]?.blogName || 'Portal'}
            </h3>
            <p className="text-xs text-slate-400 mt-1 font-medium">
              Matérias aprofundadas selecionadas exclusivamente para você pela nossa equipe.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
          {related.map((post) => {
            return (
              <Link
                key={post.id}
                href={`/blog/${post.slug}`}
                className="group block bg-slate-900/80 backdrop-blur-md border border-slate-800 rounded-3xl overflow-hidden hover:border-cyan-500/60 transition-all duration-300 shadow-xl hover:shadow-[0_10px_30px_rgba(6,182,212,0.15)] hover:-translate-y-2 flex flex-col justify-between"
              >
                <div>
                  <div className="h-44 w-full bg-slate-950 relative overflow-hidden">
                    {post.coverImage ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={post.coverImage}
                        alt={post.title}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out"
                      />
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 bg-gradient-to-br from-slate-950 to-slate-900">
                        <span className="text-2xl opacity-30 mb-2">📰</span>
                        <span className="text-[10px] uppercase font-bold tracking-widest">Sem Imagem</span>
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent pointer-events-none" />

                    {/* BADGE DE PORTAL LOCAL */}
                    <div className="absolute top-3 left-3 z-10">
                      <span className="bg-cyan-950/90 text-cyan-300 border border-cyan-500/40 px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider shadow-lg backdrop-blur-md flex items-center gap-1.5">
                        <span className="text-white">✦</span>
                        Ler Matéria
                      </span>
                    </div>
                  </div>
                  <div className="p-6">
                    <h4 className="text-sm font-bold text-slate-200 group-hover:text-cyan-400 transition-colors leading-relaxed line-clamp-3 mb-3">
                      {post.title}
                    </h4>
                  </div>
                </div>
                <div className="p-6 pt-0">
                  <div className="flex items-center justify-between text-[10px] text-slate-500 uppercase tracking-widest font-bold border-t border-slate-800/80 pt-4">
                    <span>{new Date(post.createdAt).toLocaleDateString('pt-BR')}</span>
                    <span className="flex items-center gap-1 text-cyan-400 font-black">
                      Acessar ↗
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}
