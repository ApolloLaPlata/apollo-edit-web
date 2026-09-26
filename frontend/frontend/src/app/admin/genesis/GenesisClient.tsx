'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface GenesisLog {
  id: string;
  blogId: string;
  blogName: string;
  categoryName: string;
  categorySlug: string;
  actionType: 'category_genesis' | 'niche_colonization' | 'monetization_injection';
  details: string;
  createdAt: string;
}

interface Stats {
  totalGenesis: number;
  totalColonizations: number;
  totalMonetizations: number;
  totalCategories: number;
}

export default function GenesisClient() {
  const [logs, setLogs] = useState<GenesisLog[]>([]);
  const [stats, setStats] = useState<Stats>({ totalGenesis: 0, totalColonizations: 0, totalMonetizations: 0, totalCategories: 12 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/admin/genesis?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('Erro ao buscar logs de gênese territorial:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 15000);
    return () => clearInterval(interval);
  }, [selectedBlog]);

  const handleAction = async (action: string) => {
    setActionLoading(action);
    setToast({ message: '⏳ Ativando Motor de Expansão Territorial e avaliando novas fronteiras no SQLite...', type: 'info' });

    try {
      const res = await fetch('/api/admin/genesis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog })
      });
      const data = await res.json();

      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Ciclo de expansão territorial acionado com sucesso!'}`, type: 'success' });
        await fetchLogs();
      } else {
        setToast({ message: `❌ Erro: ${data.error || 'Falha no motor de gênese.'}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro de rede: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const getActionBadge = (type: string) => {
    switch (type) {
      case 'category_genesis':
        return <span className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/50 text-amber-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🌟 GÊNESE DE TERRITÓRIO</span>;
      case 'niche_colonization':
        return <span className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/50 text-purple-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🚩 COLONIZAÇÃO DE NICHO</span>;
      case 'monetization_injection':
        return <span className="bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/50 text-emerald-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">💰 MONETIZAÇÃO VIP</span>;
      default:
        return <span className="bg-slate-500/20 border border-slate-500/40 text-slate-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">🌟 EXPANSÃO EDITORIAL</span>;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* CABEÇALHO CYBERPUNK DE LUXO */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-amber-950/60 to-slate-900 border border-amber-500/30 p-8 shadow-2xl shadow-amber-950/50">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/20 border border-amber-400/30 text-amber-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span>
              FASE 135 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              🌟 Gênese Territorial & Colonização de Nichos
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              A capacidade reprodutiva e expansiva da Colmeia. Cria novas categorias editoriais no SQLite ao detectar assuntos emergentes na internet, coloniza nichos vazios com artigos fundadores e injeta links de afiliados autonomamente.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleAction('force_full_genesis')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white font-bold rounded-2xl shadow-lg shadow-amber-600/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
            >
              {actionLoading === 'force_full_genesis' ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>🌟</span>
              )}
              <span>Forçar Ciclo de Expansão Agora</span>
            </button>

            <button
              onClick={() => handleAction('force_category_genesis')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-amber-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm"
              title="Cria novas categorias editoriais no banco se houver assunto quente"
            >
              <span>🧬</span> Criar Novas Categorias
            </button>

            <button
              onClick={() => handleAction('force_colonization')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-purple-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm"
              title="Redige matérias fundadores para nichos recém-criados"
            >
              <span>🚩</span> Colonizar Nichos
            </button>

            <button
              onClick={() => handleAction('force_monetization')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-emerald-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm"
              title="Injeta Cards VIP de recomendação de produtos afiliados"
            >
              <span>💰</span> Injetar Monetização
            </button>
          </div>
        </div>
      </div>

      {/* STATS DE EXPANSÃO TERRITORIAL */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-amber-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🌟 Categorias Criadas pela IA</div>
          <div className="text-3xl font-black text-amber-400 mt-2">{stats.totalGenesis}</div>
          <div className="text-xs text-amber-400/80 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            Territórios gerados autonomamente
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-purple-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🚩 Nichos Colonizados</div>
          <div className="text-3xl font-black text-purple-400 mt-2">{stats.totalColonizations}</div>
          <div className="text-xs text-slate-400 mt-2">
            Artigos fundadores redigidos
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">💰 Artigos Monetizados</div>
          <div className="text-3xl font-black text-emerald-400 mt-2">{stats.totalMonetizations}</div>
          <div className="text-xs text-emerald-400/80 mt-2">
            Cards VIP de afiliados acoplados
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-amber-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🏰 Total de Territórios na Rede</div>
          <div className="text-3xl font-black text-white mt-2 flex items-center gap-2">
            <span>{stats.totalCategories}</span>
            <span className="text-xs bg-amber-950 border border-amber-500/40 text-amber-300 px-2 py-0.5 rounded-full font-bold">Ativos</span>
          </div>
          <div className="text-xs text-slate-400 mt-2">
            Acervo editorial em expansão
          </div>
        </div>
      </div>

      {/* FILTROS E CONTROLES */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50 border border-slate-800 p-4 rounded-2xl">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Filtrar por Portal:</label>
          <select
            value={selectedBlog}
            onChange={(e) => setSelectedBlog(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-amber-500 transition-all font-medium"
          >
            <option value="all">🌐 Todos os Portais da Rede</option>
            <option value="descarga">📥 Descarga News</option>
            <option value="darktrap">🎵 Dark Trap Radio</option>
            <option value="macaco">🐒 Macaco Driver</option>
            <option value="classico">📜 Portal Clássico</option>
          </select>
        </div>

        <button
          onClick={() => handleAction('clear_logs')}
          disabled={actionLoading !== null || logs.length === 0}
          className="text-xs text-slate-500 hover:text-red-400 transition-colors font-semibold flex items-center gap-1.5 disabled:opacity-30"
        >
          <span>🧹</span> Limpar Telemetria de Expansão
        </button>
      </div>

      {/* FEED DE GÊNESE E COLONIZAÇÃO (TIMELINE) */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>🌟</span> Registro de Nascimento de Nichos e Conquistas de Território
        </h2>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium">Sincronizando expansão territorial no SQLite...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <div className="text-4xl mb-3">🌟</div>
            <h3 className="text-lg font-bold text-slate-300">Nenhum território novo colonizado recentemente!</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
              O seu acervo editorial está estabilizado. Clique em &quot;Forçar Ciclo de Expansão Agora&quot; para permitir que a IA avalie novas tendências na internet e crie categorias no banco.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {logs.map((log) => (
              <div
                key={log.id}
                className="bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 rounded-2xl p-6 transition-all shadow-md relative overflow-hidden"
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-4 border-b border-slate-800/60 pb-4">
                  <div className="flex flex-wrap items-center gap-3">
                    {getActionBadge(log.actionType)}
                    <span className="bg-slate-800 text-amber-300 px-3 py-1 rounded-lg text-xs font-bold">
                      🏛️ {log.blogName}
                    </span>
                    <span className="bg-slate-900 border border-slate-800 text-slate-300 px-3 py-1 rounded-lg text-xs font-mono">
                      📁 {log.categoryName} ({log.categorySlug})
                    </span>
                  </div>

                  <span className="text-slate-500 text-xs font-mono">
                    🕒 {log.createdAt}
                  </span>
                </div>

                <div className="space-y-3">
                  <div className="bg-slate-900/90 border border-amber-500/20 rounded-xl p-4 relative">
                    <div className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <span>🌟</span> Detalhes da Expansão Neural:
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed font-mono">
                      {log.details}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
