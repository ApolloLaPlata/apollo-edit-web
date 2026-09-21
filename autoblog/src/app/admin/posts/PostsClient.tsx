'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

interface PostItem {
  id: string;
  title: string;
  slug: string;
  createdAt: string;
  isPublished: number | boolean;
  author: string;
  views: number;
  blogName: string;
  blogDomain: string;
}

export default function PostsClient({ initialPosts }: { initialPosts: PostItem[] }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'published' | 'draft' | 'quarantine'>('all');
  const router = useRouter();

  const handleApprove = async (postId: string) => {
    try {
      const res = await fetch('/api/admin/posts/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ postId }),
      });
      if (res.ok) {
        // Recarrega a página para atualizar os dados
        router.refresh();
        // Fallback visual para atualizar a UI local sem refresh duro
        window.location.reload(); 
      }
    } catch (e) {
      console.error(e);
    }
  };

  const filteredPosts = useMemo(() => {
    return initialPosts.filter((post) => {
      const matchesSearch =
        post.title.toLowerCase().includes(search.toLowerCase()) ||
        (post.author && post.author.toLowerCase().includes(search.toLowerCase())) ||
        (post.blogName && post.blogName.toLowerCase().includes(search.toLowerCase()));

      const status = Number(post.isPublished); // 0=draft, 1=published, 2=quarantine
      if (filter === 'published' && status !== 1) return false;
      if (filter === 'draft' && status !== 0) return false;
      if (filter === 'quarantine' && status !== 2) return false;

      return matchesSearch;
    });
  }, [initialPosts, search, filter]);

  const pubCount = initialPosts.filter((p) => Number(p.isPublished) === 1).length;
  const draftCount = initialPosts.filter((p) => Number(p.isPublished) === 0).length;
  const quarantineCount = initialPosts.filter((p) => Number(p.isPublished) === 2).length;

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-blue-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            REDAÇÃO NEURAL & GESTÃO DE CONTEÚDO
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Acervo e Artigos da Rede
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Gerencie, edite e revise as publicações orquestradas pelo enxame de Inteligência Artificial ou crie pautas manuais para seus veículos.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link
            href="/admin"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Painel Central
          </Link>
          <Link
            href="/admin/planner"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/20 hover:scale-105 active:scale-95 flex items-center gap-2"
          >
            <span>⚡</span> Nova Pauta Neural
          </Link>
        </div>
      </div>

      {/* BARRA DE FILTROS E PESQUISA */}
      <div className="bg-slate-900/60 backdrop-blur-xl p-5 rounded-2xl border border-slate-800/80 shadow-xl flex flex-col md:flex-row justify-between items-center gap-4">
        
        {/* ABAS DE STATUS */}
        <div className="flex items-center gap-1 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 w-full md:w-auto">
          {[
            { id: 'all', label: 'Todos', count: initialPosts.length },
            { id: 'published', label: 'Publicados', count: pubCount },
            { id: 'draft', label: 'Rascunhos', count: draftCount },
            { id: 'quarantine', label: 'Quarentena / YMYL', count: quarantineCount },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setFilter(tab.id as any)}
              className={`flex-1 md:flex-initial px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
                filter === tab.id
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
              }`}
            >
              <span>{tab.label}</span>
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-mono ${filter === tab.id ? 'bg-blue-700 text-white' : 'bg-slate-800 text-slate-400'}`}>
                {tab.count}
              </span>
            </button>
          ))}
        </div>

        {/* CAMPO DE PESQUISA */}
        <div className="relative w-full md:w-80">
          <input
            type="text"
            placeholder="Pesquisar por título, autor ou portal..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 pl-10 text-xs font-medium text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
          <svg className="w-4 h-4 text-slate-500 absolute left-3.5 top-3 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 text-xs font-bold"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* TABELA EXECUTIVA */}
      <div className="bg-slate-900/60 backdrop-blur-2xl border border-slate-800/80 rounded-3xl shadow-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[800px]">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px] font-bold bg-slate-950/60">
                <th className="py-4 px-6">Título do Artigo</th>
                <th className="py-4 px-6">Portal</th>
                <th className="py-4 px-6">Autor (IA / Redação)</th>
                <th className="py-4 px-6 text-right">Leituras</th>
                <th className="py-4 px-6 text-center">Status</th>
                <th className="py-4 px-6">Data de Publicação</th>
                <th className="py-4 px-6 text-right">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-sm">
              {filteredPosts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-16 text-center text-slate-500">
                    <div className="w-12 h-12 rounded-2xl bg-slate-950/80 border border-slate-800 flex items-center justify-center mx-auto mb-3 text-2xl">
                      📝
                    </div>
                    <p className="font-bold text-slate-300 text-sm">Nenhum artigo encontrado</p>
                    <p className="text-xs text-slate-500 mt-1">
                      {search ? `Sem resultados para "${search}".` : 'Nenhuma publicação registrada nesta categoria.'}
                    </p>
                  </td>
                </tr>
              ) : (
                filteredPosts.map((post) => {
                  const isPub = Boolean(post.isPublished);
                  return (
                    <tr key={post.id} className="hover:bg-slate-800/40 transition-colors group">
                      
                      {/* TÍTULO & SLUG */}
                      <td className="py-4 px-6 max-w-sm">
                        <div className="font-bold text-white group-hover:text-blue-400 transition-colors truncate" title={post.title}>
                          {post.title}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-[11px] font-mono text-slate-500 truncate max-w-[200px]">/{post.slug}</span>
                          {isPub && post.blogDomain && (
                            <a
                              href={`https://${post.blogDomain}/blog/${post.slug}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[10px] text-blue-400/80 hover:text-blue-300 hover:underline inline-flex items-center gap-0.5"
                            >
                              Ver no site ↗
                            </a>
                          )}
                        </div>
                      </td>

                      {/* PORTAL */}
                      <td className="py-4 px-6">
                        <span className="inline-flex items-center gap-1.5 bg-slate-950/80 text-xs px-3 py-1 rounded-lg text-slate-300 border border-slate-800 font-medium">
                          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                          {post.blogName || 'Global'}
                        </span>
                      </td>

                      {/* AUTOR */}
                      <td className="py-4 px-6 text-slate-300 font-medium text-xs">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-slate-400">
                            {post.author ? post.author.charAt(0).toUpperCase() : 'A'}
                          </div>
                          <span>{post.author || 'Agente Neural'}</span>
                        </div>
                      </td>

                      {/* LEITURAS (REAL DATA) */}
                      <td className="py-4 px-6 text-right font-mono font-bold text-slate-300">
                        {(post.views || 0).toLocaleString('pt-BR')}
                      </td>

                      {/* STATUS */}
                      <td className="py-4 px-6 text-center">
                        <span
                          className={`inline-flex items-center gap-1.5 px-3 py-1 text-[11px] font-bold rounded-full border ${
                            post.isPublished === 1
                              ? 'bg-emerald-950/60 text-emerald-400 border-emerald-500/30'
                              : post.isPublished === 2
                              ? 'bg-purple-950/60 text-purple-400 border-purple-500/30'
                              : 'bg-amber-950/60 text-amber-400 border-amber-500/30'
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              post.isPublished === 1 ? 'bg-emerald-400 animate-pulse' : post.isPublished === 2 ? 'bg-purple-400 animate-ping' : 'bg-amber-400'
                            }`}
                          />
                          {post.isPublished === 1 ? 'Publicado' : post.isPublished === 2 ? 'Revisão (YMYL)' : 'Rascunho'}
                        </span>
                      </td>

                      {/* DATA */}
                      <td className="py-4 px-6 text-slate-400 font-mono text-xs">
                        {new Date(post.createdAt).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>

                      {/* AÇÕES */}
                      <td className="py-4 px-6 text-right flex justify-end gap-2">
                        {post.isPublished === 2 && (
                          <button
                            onClick={() => handleApprove(post.id)}
                            className="px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white transition-all shadow-[0_0_10px_rgba(147,51,234,0.3)]"
                          >
                            Liberar ✓
                          </button>
                        )}
                        <Link
                          href={`/admin/posts/${post.id}`}
                          className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-blue-600 text-xs font-bold text-slate-300 hover:text-white transition-all border border-slate-700 hover:border-blue-500 shadow-sm inline-block"
                        >
                          Editar →
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
