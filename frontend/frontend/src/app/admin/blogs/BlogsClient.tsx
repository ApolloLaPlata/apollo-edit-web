'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';

interface BlogItem {
  id: string;
  name: string;
  domain: string;
  niche: string;
  description: string;
  theme: string;
  agentConfig: {
    id: string;
    isActive: number | boolean;
    postFrequency: number;
  } | null;
  _count: {
    posts: number;
  };
}

export default function BlogsClient({ initialBlogs }: { initialBlogs: BlogItem[] }) {
  const [blogs, setBlogs] = useState<BlogItem[]>(initialBlogs);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'active' | 'paused'>('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  const [form, setForm] = useState({
    name: '',
    domain: '',
    niche: '',
    postFrequency: 3,
  });

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const refreshBlogs = async () => {
    try {
      const res = await fetch('/api/admin/blogs');
      const data = await res.json();
      if (data.success && data.blogs) {
        setBlogs(data.blogs);
      }
    } catch (err) {
      console.error('Erro ao atualizar lista de portais:', err);
    }
  };

  const handleCreateBlog = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim() || !form.domain.trim() || !form.niche.trim()) return;
    
    setLoading(true);
    try {
      const res = await fetch('/api/admin/blogs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      
      if (data.success || res.ok) {
        setIsModalOpen(false);
        setForm({ name: '', domain: '', niche: '', postFrequency: 3 });
        await refreshBlogs();
        showNotification('success', 'Nova franquia provisionada com sucesso na rede autônoma!');
      } else {
        showNotification('error', data.error || 'Falha ao provisionar portal.');
      }
    } catch (err) {
      showNotification('error', 'Erro de conexão ao tentar criar veículo.');
    } finally {
      setLoading(false);
    }
  };

  const filteredBlogs = useMemo(() => {
    return blogs.filter((blog) => {
      const matchesSearch =
        blog.name.toLowerCase().includes(search.toLowerCase()) ||
        blog.domain.toLowerCase().includes(search.toLowerCase()) ||
        blog.niche.toLowerCase().includes(search.toLowerCase());

      const isActive = Boolean(blog.agentConfig?.isActive);
      if (filter === 'active' && !isActive) return false;
      if (filter === 'paused' && isActive) return false;

      return matchesSearch;
    });
  }, [blogs, search, filter]);

  const activeCount = blogs.filter((b) => Boolean(b.agentConfig?.isActive)).length;
  const pausedCount = blogs.length - activeCount;

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* BANNER DE NOTIFICAÇÃO EXECUTIVA */}
      {notification && (
        <div
          className={`p-4 rounded-2xl border flex items-center justify-between shadow-xl transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
              : notification.type === 'error'
              ? 'bg-red-950/80 border-red-500/40 text-red-300'
              : 'bg-blue-950/80 border-blue-500/40 text-blue-300'
          }`}
        >
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="text-base">
              {notification.type === 'success' ? '✓' : notification.type === 'error' ? '⚠️' : 'ℹ️'}
            </span>
            <span>{notification.message}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2">
            ✕
          </button>
        </div>
      )}

      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-blue-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            FROTA MULTI-TENANT • PORTAIS ISOLADOS
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Gestão de Veículos & Franquias
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Administre todos os veículos de comunicação da rede. Cada portal opera com seu próprio Agente Neural independente, design agnóstico e regras exclusivas de monetização.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link
            href="/admin"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Painel Central
          </Link>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/20 hover:scale-105 active:scale-95 flex items-center gap-2"
          >
            <span>➕</span> Criar Novo Veículo (Franquia)
          </button>
        </div>
      </div>

      {/* DASHBOARD GLOBAL (FASE 86) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900/60 p-6 rounded-3xl border border-emerald-500/20 shadow-lg relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 text-7xl opacity-5 group-hover:scale-110 transition-transform">💰</div>
          <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-widest mb-1">Faturamento Global</h3>
          <p className="text-3xl font-black text-white tracking-tighter">R$ 14.892<span className="text-sm font-normal text-slate-500 ml-1">/mês</span></p>
          <p className="text-xs text-slate-400 mt-2">Soma de Ads, Paywall e Afiliados</p>
        </div>
        <div className="bg-slate-900/60 p-6 rounded-3xl border border-cyan-500/20 shadow-lg relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 text-7xl opacity-5 group-hover:scale-110 transition-transform">📈</div>
          <h3 className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-1">Tráfego da Rede</h3>
          <p className="text-3xl font-black text-white tracking-tighter">1.2M<span className="text-sm font-normal text-slate-500 ml-1">views</span></p>
          <p className="text-xs text-slate-400 mt-2">+45% vs mês passado (SEO Orgânico)</p>
        </div>
        <div className="bg-slate-900/60 p-6 rounded-3xl border border-purple-500/20 shadow-lg relative overflow-hidden group">
          <div className="absolute -right-6 -top-6 text-7xl opacity-5 group-hover:scale-110 transition-transform">🧠</div>
          <h3 className="text-xs font-bold text-purple-400 uppercase tracking-widest mb-1">Leads Compartilhados</h3>
          <p className="text-3xl font-black text-white tracking-tighter">84.5K<span className="text-sm font-normal text-slate-500 ml-1">ativos</span></p>
          <p className="text-xs text-slate-400 mt-2">Disponíveis para Retargeting Mútuo</p>
        </div>
      </div>

      {/* BARRA DE PESQUISA E FILTROS */}
      <div className="bg-slate-900/60 backdrop-blur-xl p-5 rounded-2xl border border-slate-800/80 shadow-xl flex flex-col md:flex-row justify-between items-center gap-4">
        
        {/* ABAS DE STATUS */}
        <div className="flex items-center gap-1 bg-slate-950/80 p-1.5 rounded-xl border border-slate-800 w-full md:w-auto">
          {[
            { id: 'all', label: 'Todos os Portais', count: blogs.length },
            { id: 'active', label: 'IA Ligada (Ativos)', count: activeCount },
            { id: 'paused', label: 'IA Em Espera', count: pausedCount },
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
            placeholder="Pesquisar por nome, domínio ou nicho..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 pl-10 text-xs font-medium text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
          <svg className="w-4 h-4 text-slate-500 absolute left-3.5 top-3 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          {search && (
            <button onClick={() => setSearch('')} className="absolute right-3 top-2.5 text-slate-500 hover:text-slate-300 text-xs font-bold">
              ✕
            </button>
          )}
        </div>
      </div>

      {/* GRID DE CARDS DE PORTAIS */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredBlogs.length === 0 ? (
          <div className="col-span-full py-20 text-center text-slate-500 bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-dashed border-slate-800 flex flex-col items-center justify-center">
            <div className="w-14 h-14 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-3xl mb-4">
              🏗️
            </div>
            <h2 className="text-base font-bold text-slate-300 mb-1">Nenhum portal encontrado</h2>
            <p className="text-xs text-slate-500 max-w-sm">
              {search ? `Sem resultados para "${search}".` : 'Crie seu primeiro portal na rede para iniciar a geração autônoma.'}
            </p>
          </div>
        ) : (
          filteredBlogs.map((blog) => {
            const isActive = Boolean(blog.agentConfig?.isActive);
            return (
              <div
                key={blog.id}
                className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl flex flex-col justify-between transition-all hover:border-slate-700 hover:shadow-2xl group relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl -mr-16 -mt-16 group-hover:bg-blue-500/10 transition-colors pointer-events-none" />

                <div>
                  <div className="flex justify-between items-start mb-6">
                    <div className="flex items-center gap-4 min-w-0 pr-2">
                      <div
                        className={`w-12 h-12 rounded-2xl flex items-center justify-center text-xl shrink-0 border ${
                          isActive
                            ? 'bg-emerald-950/80 border-emerald-500/30 text-emerald-400 shadow-sm'
                            : 'bg-slate-800 border-slate-700 text-slate-500'
                        }`}
                      >
                        {isActive ? '🤖' : '💤'}
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-extrabold text-lg text-white group-hover:text-blue-400 transition-colors truncate">
                          {blog.name}
                        </h4>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[11px] uppercase tracking-wider font-bold text-slate-400 font-mono truncate">
                            {blog.domain}
                          </span>
                        </div>
                      </div>
                    </div>

                    <a
                      href={`https://${blog.domain}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-xl bg-slate-950/80 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors border border-slate-800 shrink-0"
                      title="Abrir site no navegador ↗"
                    >
                      ↗
                    </a>
                  </div>

                  <div className="space-y-3 my-4">
                    <div className="flex justify-between items-center text-xs bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80">
                      <span className="text-slate-400 font-semibold uppercase tracking-wider">Nicho Editorial</span>
                      <span className="text-slate-200 font-bold truncate max-w-[150px]">{blog.niche}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80">
                      <span className="text-slate-400 font-semibold uppercase tracking-wider">Artigos Gerados</span>
                      <span className="text-blue-400 font-extrabold font-mono text-sm">{blog._count.posts}</span>
                    </div>
                    <div className="flex justify-between items-center text-xs bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80">
                      <span className="text-slate-400 font-semibold uppercase tracking-wider">Ritmo Biológico</span>
                      <span className="text-slate-200 font-bold font-mono">{blog.agentConfig?.postFrequency || 0} posts/dia</span>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-5 border-t border-slate-800/80 flex gap-2.5">
                  <Link
                    href={`/admin/blogs/${blog.id}`}
                    className="flex-1 text-center bg-blue-600/10 hover:bg-blue-600/20 text-blue-400 hover:text-blue-300 font-bold py-2.5 rounded-xl transition-all border border-blue-500/20 text-xs flex items-center justify-center gap-1.5"
                  >
                    <span>🧠</span>
                    <span>Cortex IA</span>
                  </Link>
                  <Link
                    href={`/admin/appearance?blogId=${blog.id}`}
                    className="bg-slate-950/80 hover:bg-slate-800 text-slate-300 hover:text-white px-4 py-2.5 rounded-xl transition-all text-xs font-bold border border-slate-800 flex items-center justify-center gap-1.5"
                    title="Aparência & Design"
                  >
                    <span>🎨</span>
                    <span>Design</span>
                  </Link>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* MODAL DE CRIAÇÃO DE NOVA FRANQUIA */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 max-w-lg w-full shadow-2xl space-y-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none -mr-24 -mt-24" />

            <div className="flex justify-between items-center border-b border-slate-800 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center text-lg">
                  ➕
                </div>
                <div>
                  <h3 className="font-extrabold text-lg text-white">Provisionar Nova Franquia</h3>
                  <p className="text-xs text-slate-400">O portal será integrado à rede e à IA central.</p>
                </div>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center text-xs font-bold transition-colors"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleCreateBlog} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Nome do Veículo / Portal
                </label>
                <input
                  type="text"
                  placeholder="Ex: Tech Pulse News"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-medium text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Domínio Oficial (sem https://)
                </label>
                <input
                  type="text"
                  placeholder="Ex: techpulsenews.com"
                  value={form.domain}
                  onChange={(e) => setForm({ ...form, domain: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Nicho Principal de Atuação
                </label>
                <input
                  type="text"
                  placeholder="Ex: Tecnologia, Inteligência Artificial e Inovação"
                  value={form.niche}
                  onChange={(e) => setForm({ ...form, niche: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-medium text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-all"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Ritmo Biológico (Artigos Diários pela IA)
                </label>
                <input
                  type="number"
                  min={1}
                  max={24}
                  value={form.postFrequency}
                  onChange={(e) => setForm({ ...form, postFrequency: Number(e.target.value) })}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-blue-500 transition-all"
                  required
                />
                <span className="text-[11px] text-slate-500 mt-1 block">O enxame distribuirá a redação ao longo das 24h do dia.</span>
              </div>

              <div className="pt-4 flex justify-end gap-3 border-t border-slate-800/80 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 hover:text-white transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/20 disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <span>⚡ Provisionar Franquia</span>
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
