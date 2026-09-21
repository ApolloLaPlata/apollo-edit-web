'use client';
import React, { useEffect, useState } from 'react';

export default function SyndicateClient() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<{ posts: any[]; blogs: any[]; stats: any } | null>(null);
  const [search, setSearch] = useState('');
  const [selectedBlogFilter, setSelectedBlogFilter] = useState('ALL');

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [activePost, setActivePost] = useState<any | null>(null);
  const [targetBlogId, setTargetBlogId] = useState('');
  const [customAngle, setCustomAngle] = useState('');
  const [syndicating, setSyndicating] = useState(false);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/syndicate');
      const json = await res.json();
      if (json.success) {
        setData(json);
        if (json.blogs?.length > 0) {
          setTargetBlogId(json.blogs[0].id);
        }
      } else {
        showToast('error', json.error || 'Erro ao carregar dados de sindicância.');
      }
    } catch (e) {
      showToast('error', 'Falha na conexão com o servidor de sindicância.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenModal = (post: any) => {
    setActivePost(post);
    setCustomAngle('');
    // Definir como padrão um blog diferente do atual, se houver
    if (data?.blogs) {
      const otherBlog = data.blogs.find((b: any) => b.id !== post.blogId);
      if (otherBlog) setTargetBlogId(otherBlog.id);
    }
    setModalOpen(true);
  };

  const handleSyndicate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activePost || !targetBlogId) return;

    setSyndicating(true);
    try {
      const res = await fetch('/api/admin/syndicate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sourcePostId: activePost.id,
          targetBlogId,
          customAngle,
        }),
      });
      const json = await res.json();
      if (json.success) {
        showToast('success', json.message || 'Sindicância concluída com sucesso!');
        setModalOpen(false);
        fetchData(); // Atualiza a lista e estatísticas
      } else {
        showToast('error', json.error || 'Falha ao processar sindicância.');
      }
    } catch (error) {
      showToast('error', 'Erro de rede na requisição HTTP.');
    } finally {
      setSyndicating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium text-sm tracking-wide animate-pulse">
          Sincronizando Sindicato Neural da Colmeia...
        </p>
      </div>
    );
  }

  const posts = data?.posts || [];
  const blogs = data?.blogs || [];
  const stats = data?.stats || { totalPosts: 0, totalBlogs: 0, syndicatedCount: { count: 0 } };

  const filteredPosts = posts.filter((p) => {
    const matchesSearch = p.title.toLowerCase().includes(search.toLowerCase()) || p.blogName?.toLowerCase().includes(search.toLowerCase());
    const matchesBlog = selectedBlogFilter === 'ALL' || p.blogId === selectedBlogFilter;
    return matchesSearch && matchesBlog;
  });

  return (
    <div className="space-y-10 relative">
      {/* TOAST EXECUTIVO */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/90 border-red-500/50 text-red-300'
          }`}
        >
          <span className="text-lg">{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span className="text-xs font-semibold">{toast.message}</span>
          <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      {/* HEADER CORPORATIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-cyan-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              SINDICATO NEURAL • CROSS-CHANNEL SYNDICATION
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Sindicato & Cross-Post da Frota
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Replique, adapte e distribua reportagens de alto engajamento entre todos os seus veículos da rede. Crie backlinks internos de alta autoridade e potencialize o tráfego orgânico sem custos adicionais.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Frota Ativa</span>
              <span className="text-2xl font-extrabold text-white font-mono">{stats.totalBlogs}</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Reportagens</span>
              <span className="text-2xl font-extrabold text-blue-400 font-mono">{stats.totalPosts}</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Sindicados</span>
              <span className="text-2xl font-extrabold text-cyan-400 font-mono">{stats.syndicatedCount?.count || 0}</span>
            </div>
          </div>
        </div>
      </div>

      {/* BARRA DE PESQUISA E FILTROS */}
      <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80 backdrop-blur-md">
        <div className="relative w-full md:w-96">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">🔍</span>
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por título ou portal de origem..."
            className="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-800/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
          <button
            onClick={() => setSelectedBlogFilter('ALL')}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              selectedBlogFilter === 'ALL'
                ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800/80'
            }`}
          >
            Todos os Portais ({posts.length})
          </button>
          {blogs.map((b) => {
            const count = posts.filter((p) => p.blogId === b.id).length;
            return (
              <button
                key={b.id}
                onClick={() => setSelectedBlogFilter(b.id)}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  selectedBlogFilter === b.id
                    ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                    : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800/80'
                }`}
              >
                {b.name} ({count})
              </button>
            );
          })}
        </div>
      </div>

      {/* TABELA / GRID DE ARTIGOS DISPONÍVEIS PARA SINDICÂNCIA */}
      <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-slate-800/80 overflow-hidden shadow-2xl">
        <div className="p-6 border-b border-slate-800/80 flex justify-between items-center">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>⚡</span> Inventário Geral de Conteúdo para Cross-Post
          </h2>
          <span className="text-xs text-slate-400 font-mono">Exibindo {filteredPosts.length} reportagens</span>
        </div>

        {filteredPosts.length === 0 ? (
          <div className="p-16 text-center text-slate-500 font-medium">
            <span className="text-4xl block mb-3 opacity-30">📂</span>
            Nenhuma reportagem encontrada para este filtro.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800/80 text-[10px] uppercase tracking-widest text-slate-500 bg-slate-950/40">
                  <th className="p-4 font-bold">Reportagem / Artigo</th>
                  <th className="p-4 font-bold">Portal de Origem</th>
                  <th className="p-4 font-bold">Status</th>
                  <th className="p-4 font-bold">Data</th>
                  <th className="p-4 font-bold text-right">Ação Neural</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-slate-800/50">
                {filteredPosts.map((post) => {
                  const isSyndicated = post.author === 'Sindicato Neural Apollo' || post.slug.includes('-syndicated-');
                  return (
                    <tr key={post.id} className="hover:bg-slate-800/40 transition-colors group">
                      <td className="p-4 max-w-md">
                        <div className="flex items-center gap-3">
                          {post.coverImage ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={post.coverImage} alt="" className="w-10 h-10 rounded-lg object-cover bg-slate-800 shrink-0 border border-slate-700/50" />
                          ) : (
                            <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-xs text-slate-500 shrink-0 font-bold">
                              📄
                            </div>
                          )}
                          <div className="truncate">
                            <p className="font-bold text-white group-hover:text-cyan-400 transition-colors truncate">
                              {post.title}
                            </p>
                            <span className="text-[10px] font-mono text-slate-500">/{post.slug}</span>
                          </div>
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="bg-slate-950/80 px-3 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-wider text-cyan-300 border border-cyan-900/50">
                          {post.blogName || post.blogDomain}
                        </span>
                      </td>
                      <td className="p-4">
                        {isSyndicated ? (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-purple-500/10 text-purple-300 border border-purple-500/20">
                            <span>⚡</span> Sindicado
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            <span>✓</span> Original
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-xs font-mono text-slate-400">
                        {new Date(post.createdAt).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => handleOpenModal(post)}
                          className="bg-cyan-600/20 hover:bg-cyan-600 text-cyan-300 hover:text-white px-4 py-2 rounded-xl text-xs font-bold transition-all border border-cyan-500/30 hover:border-cyan-500 shadow-sm active:scale-95"
                        >
                          ⚡ Sindicar para outro Veículo
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* MODAL DE SINDICÂNCIA NEURAL */}
      {modalOpen && activePost && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700/80 rounded-3xl shadow-2xl w-full max-w-lg p-8 space-y-6 animate-in zoom-in-95 duration-200 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none -mr-16 -mt-16" />

            <div className="flex justify-between items-start">
              <div>
                <span className="text-[10px] font-black uppercase tracking-widest text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-md border border-cyan-500/20">
                  Cross-Channel Action
                </span>
                <h3 className="text-xl font-extrabold text-white mt-2">Sindicar Reportagem</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Selecione o portal que receberá esta matéria e ajuste o ângulo editorial.
                </p>
              </div>
              <button
                onClick={() => setModalOpen(false)}
                className="w-8 h-8 rounded-full bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            <div className="bg-slate-950/80 p-4 rounded-2xl border border-slate-800/80 space-y-1">
              <span className="text-[10px] uppercase font-bold text-slate-500">Artigo de Origem</span>
              <p className="text-sm font-bold text-white line-clamp-2">{activePost.title}</p>
              <p className="text-[10px] text-cyan-400 font-mono">Portal: {activePost.blogName}</p>
            </div>

            <form onSubmit={handleSyndicate} className="space-y-5">
              <div>
                <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider mb-2">
                  Portal de Destino (Alvo)
                </label>
                <select
                  value={targetBlogId}
                  onChange={(e) => setTargetBlogId(e.target.value)}
                  required
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-white text-sm font-bold focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
                >
                  {blogs.map((b) => (
                    <option key={b.id} value={b.id} disabled={b.id === activePost.blogId}>
                      {b.name} ({b.domain}) {b.id === activePost.blogId ? ' — [ORIGEM]' : ''}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider mb-2">
                  Ângulo ou Sufixo Editorial (Opcional)
                </label>
                <input
                  type="text"
                  value={customAngle}
                  onChange={(e) => setCustomAngle(e.target.value)}
                  placeholder="Ex: Análise Exclusiva Finanças ou Destaque Especial"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                />
                <span className="text-[10px] text-slate-500 mt-1 block font-medium">
                  Se deixado em branco, o sistema adicionará a tag [Edição Nome do Portal].
                </span>
              </div>

              <div className="flex gap-3 pt-4 border-t border-slate-800/80">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  disabled={syndicating}
                  className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-bold py-3.5 rounded-xl transition-colors text-xs uppercase tracking-wider"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={syndicating || !targetBlogId || targetBlogId === activePost.blogId}
                  className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white font-black py-3.5 rounded-xl shadow-lg shadow-cyan-500/20 transition-all text-xs uppercase tracking-wider flex items-center justify-center gap-2 active:scale-95"
                >
                  {syndicating ? (
                    <>
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Sindicando...
                    </>
                  ) : (
                    <>
                      <span>⚡</span> Executar Sindicância Neural
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
