'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface ImmuneLog {
  id: string;
  blogId: string;
  blogName: string;
  postId: string;
  postTitle: string;
  actionType: 'regeneration' | 'image_healing' | 'audience_adaptation';
  details: string;
  scoreBefore?: number;
  scoreAfter?: number;
  createdAt: string;
}

interface Stats {
  totalRegenerations: number;
  totalAdaptations: number;
  healthScore: string;
  healthPercentage: number;
}

export default function ImmuneClient() {
  const [logs, setLogs] = useState<ImmuneLog[]>([]);
  const [stats, setStats] = useState<Stats>({ totalRegenerations: 0, totalAdaptations: 0, healthScore: '9.8', healthPercentage: 98 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/admin/immune?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('Erro ao buscar logs imunológicos:', e);
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
    setToast({ message: '⏳ Ativando glóbulos brancos editoriais e varrendo o acervo da Colmeia...', type: 'info' });

    try {
      const res = await fetch('/api/admin/immune', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog })
      });
      const data = await res.json();

      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Ciclo de cura imunológica acionado com sucesso!'}`, type: 'success' });
        await fetchLogs();
      } else {
        setToast({ message: `❌ Erro: ${data.error || 'Falha na varredura imunológica.'}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro de rede: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const getActionBadge = (type: string) => {
    switch (type) {
      case 'regeneration':
        return <span className="bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/50 text-emerald-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🩺 REGENERAÇÃO DE TECIDO (SELF-HEALING)</span>;
      case 'audience_adaptation':
        return <span className="bg-gradient-to-r from-blue-500/20 to-indigo-500/20 border border-blue-500/50 text-blue-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🧬 ADAPTAÇÃO POR AUDIÊNCIA</span>;
      default:
        return <span className="bg-slate-500/20 border border-slate-500/40 text-slate-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">🛡️ IMUNIDADE EDITORIAL</span>;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* CABEÇALHO CYBERPUNK DE LUXO */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-emerald-950/60 to-slate-900 border border-emerald-500/30 p-8 shadow-2xl shadow-emerald-950/50">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              FASE 134 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              🛡️ Sistema Imunológico & Saúde do Acervo
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              O escudo biológico da Colmeia. Varre continuamente o banco SQLite regenerando matérias curtas ou sem capa, e adapta o foco editorial ao vivo observando o comportamento da audiência.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleAction('force_full_immune')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-2xl shadow-lg shadow-emerald-600/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
            >
              {actionLoading === 'force_full_immune' ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>🛡️</span>
              )}
              <span>Forçar Varredura Imunológica</span>
            </button>

            <button
              onClick={() => handleAction('force_regeneration')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-emerald-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm"
              title="Varre e regenera matérias curtas ou sem capa no SQLite"
            >
              <span>🩺</span> Regenerar Tecidos
            </button>

            <button
              onClick={() => handleAction('force_adaptation')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-blue-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm"
              title="Adapta a pauta observando a audiência dos últimos posts"
            >
              <span>🧬</span> Adaptar Foco
            </button>
          </div>
        </div>
      </div>

      {/* STATS DE SAÚDE BIOLÓGICA */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🩺 Artigos Regenerados</div>
          <div className="text-3xl font-black text-emerald-400 mt-2">{stats.totalRegenerations}</div>
          <div className="text-xs text-emerald-400/80 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            Matérias salvas e expandidas
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-blue-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🧬 Adaptações de Audiência</div>
          <div className="text-3xl font-black text-blue-400 mt-2">{stats.totalAdaptations}</div>
          <div className="text-xs text-slate-400 mt-2">
            Reinforcement learning editorial
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-teal-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🌟 Escore Médio de Saúde</div>
          <div className="text-3xl font-black text-teal-400 mt-2">⭐ {stats.healthScore}</div>
          <div className="text-xs text-teal-400/80 mt-2">
            Auditoria global do SQLite
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🛡️ Imunidade do Sistema</div>
          <div className="text-2xl font-black text-emerald-400 mt-2 flex items-center gap-2">
            <span>{stats.healthPercentage}%</span>
            <span className="text-xs bg-emerald-950 border border-emerald-500/40 text-emerald-300 px-2 py-0.5 rounded-full font-bold">Blindado</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-emerald-400 h-full transition-all duration-1000" style={{ width: `${stats.healthPercentage}%` }} />
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
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-emerald-500 transition-all font-medium"
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
          <span>🧹</span> Limpar Telemetria Imunológica
        </button>
      </div>

      {/* FEED IMUNOLÓGICO (TIMELINE) */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>🔬</span> Registro de Intervenções e Regenerações da IA
        </h2>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium">Sincronizando glóbulos brancos editoriais no SQLite...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <div className="text-4xl mb-3">🛡️</div>
            <h3 className="text-lg font-bold text-slate-300">Nenhuma anomalia ou tecido fraco detectado!</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
              O seu acervo editorial está 100% saudável. Clique em &quot;Forçar Varredura Imunológica&quot; acima para auditar o banco de dados agora.
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
                    <span className="bg-slate-800 text-emerald-300 px-3 py-1 rounded-lg text-xs font-bold">
                      🏛️ {log.blogName}
                    </span>
                    <span className="text-slate-500 text-xs font-mono">
                      🕒 {log.createdAt}
                    </span>
                  </div>

                  {log.scoreBefore && log.scoreAfter && (
                    <div className="flex items-center gap-2 bg-slate-900/90 px-3 py-1 rounded-xl border border-slate-800">
                      <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Escore Imune:</span>
                      <span className="text-xs font-bold text-slate-500">⭐ {log.scoreBefore.toFixed(1)}</span>
                      <span className="text-xs text-emerald-400 font-black">➔</span>
                      <span className="bg-emerald-950 border border-emerald-500/40 text-emerald-300 px-2 py-0.5 rounded-lg text-xs font-black">
                        ⭐ {log.scoreAfter.toFixed(1)}
                      </span>
                    </div>
                  )}
                </div>

                <div className="space-y-3">
                  <h3 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                    <span>🧬</span>
                    <span>{log.postTitle}</span>
                  </h3>

                  {/* BOX DE DETALHES DA CURA */}
                  <div className="bg-slate-900/90 border border-emerald-500/20 rounded-xl p-4 relative">
                    <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <span>🛡️</span> Intervenção do Sistema Imunológico:
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
