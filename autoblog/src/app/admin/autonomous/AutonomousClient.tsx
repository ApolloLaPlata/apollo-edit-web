'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface AutonomousLog {
  id: string;
  blogId: string;
  blogName: string;
  decisionType: 'publish_repost' | 'skip_limit' | 'self_correction' | 'external_search' | 'evaluate';
  topic: string;
  reasoning: string;
  evaluationScore: number;
  correctionsMade: string;
  repostUrl: string;
  createdAt: string;
}

interface Stats {
  totalActionsToday: number;
  repostsToday: number;
  avgQualityScore: string;
}

export default function AutonomousClient() {
  const [logs, setLogs] = useState<AutonomousLog[]>([]);
  const [stats, setStats] = useState<Stats>({ totalActionsToday: 0, repostsToday: 0, avgQualityScore: '9.8' });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/admin/autonomous?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('Erro ao buscar logs autônomos:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 15000); // Atualiza a cada 15s ao vivo
    return () => clearInterval(interval);
  }, [selectedBlog]);

  const handleAction = async (action: 'force_cycle' | 'evaluate_latest' | 'clear_logs') => {
    setActionLoading(action);
    setToast({ message: '⏳ Processando comando no motor neural da Colmeia...', type: 'info' });

    try {
      const res = await fetch('/api/admin/autonomous', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog })
      });
      const data = await res.json();

      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Comando executado com sucesso!'}`, type: 'success' });
        await fetchLogs();
      } else {
        setToast({ message: `❌ Erro: ${data.error || 'Falha na execução.'}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro de rede: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const getDecisionBadge = (type: string) => {
    switch (type) {
      case 'publish_repost':
        return <span className="bg-gradient-to-r from-red-500/20 to-orange-500/20 border border-red-500/50 text-red-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🎬 REPOSTAGEM & PUBLICADO</span>;
      case 'skip_limit':
        return <span className="bg-amber-500/20 border border-amber-500/40 text-amber-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">⚖️ CADÊNCIA PRESERVADA (LIMITE)</span>;
      case 'self_correction':
        return <span className="bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🩺 AUTOCORREÇÃO APLICADA</span>;
      case 'evaluate':
        return <span className="bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5">🛡️ AUDITORIA APROVADA</span>;
      default:
        return <span className="bg-slate-500/20 border border-slate-500/40 text-slate-300 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">🤖 AÇÃO NEURAL</span>;
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* CABEÇALHO DE LUXO */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-indigo-950/60 to-slate-900 border border-indigo-500/30 p-8 shadow-2xl shadow-indigo-950/50">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 -mb-12 -ml-12 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-500/20 border border-indigo-400/30 text-indigo-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span>
              FASE 132 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              🧠 Central de Autogestão & Repostagem
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              O motor neural inteligente que pesquisa vídeos no YouTube e pautas quentes da internet, decide o editorial de cada portal, redige matérias, autocorrige e posta 24/7 sem intervenção manual.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleAction('force_cycle')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-bold rounded-2xl shadow-lg shadow-indigo-600/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
            >
              {actionLoading === 'force_cycle' ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>🚀</span>
              )}
              <span>Forçar Ciclo Autônomo Agora</span>
            </button>

            <button
              onClick={() => handleAction('evaluate_latest')}
              disabled={actionLoading !== null}
              className="px-5 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50"
              title="A IA revisa e autocorrige o último artigo publicado"
            >
              {actionLoading === 'evaluate_latest' ? (
                <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>🩺</span>
              )}
              <span>Auditar & Autocorrigir Último Post</span>
            </button>
          </div>
        </div>
      </div>

      {/* STATS NEURAIS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-indigo-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">⚡ Ações & Decisões Hoje</div>
          <div className="text-3xl font-black text-white mt-2">{stats.totalActionsToday}</div>
          <div className="text-xs text-indigo-400 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            Autogestão contínua no banco SQLite
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-red-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🎬 Repostagens do YouTube</div>
          <div className="text-3xl font-black text-red-400 mt-2">{stats.repostsToday}</div>
          <div className="text-xs text-slate-400 mt-2">
            Cruzamento de mídia omni-channel
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-emerald-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🛡️ Nota Média Editorial</div>
          <div className="text-3xl font-black text-emerald-400 mt-2">⭐ {stats.avgQualityScore} <span className="text-sm font-normal text-slate-400">/ 10</span></div>
          <div className="text-xs text-emerald-400/80 mt-2">
            Auditado pelo modelo Qwen 72B
          </div>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 relative overflow-hidden group hover:border-cyan-500/50 transition-all">
          <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">🛰️ Piloto Automático 24/7</div>
          <div className="text-lg font-bold text-cyan-400 mt-2 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></span>
            100% Autônomo
          </div>
          <div className="text-xs text-slate-400 mt-2">
            Pulso cron e heurística sem intervenção
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
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-indigo-500 transition-all font-medium"
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
          <span>🧹</span> Limpar Histórico de Telemetria
        </button>
      </div>

      {/* FEED DE DECISÕES (TIMELINE) */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>📜</span> Histórico de Decisões e Pensamento da IA
        </h2>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <div className="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium">Sincronizando pensamentos editoriais no banco SQLite...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <div className="text-4xl mb-3">🤖</div>
            <h3 className="text-lg font-bold text-slate-300">Nenhuma decisão registrada neste filtro</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
              O motor autônomo executa análises periódicas. Clique no botão &quot;Forçar Ciclo Autônomo Agora&quot; acima para acionar uma decisão editorial imediata.
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
                    {getDecisionBadge(log.decisionType)}
                    <span className="bg-slate-800 text-indigo-300 px-3 py-1 rounded-lg text-xs font-bold">
                      🏛️ {log.blogName}
                    </span>
                    <span className="text-slate-500 text-xs font-mono">
                      🕒 {log.createdAt}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Nota IA:</span>
                    <span className="bg-emerald-950 border border-emerald-500/40 text-emerald-300 px-2.5 py-0.5 rounded-lg text-xs font-black">
                      ⭐ {log.evaluationScore ? log.evaluationScore.toFixed(1) : '10.0'}
                    </span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <span>📰</span>
                      <span>{log.topic}</span>
                    </h3>
                    {log.repostUrl && (
                      <a
                        href={log.repostUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 mt-1 font-semibold hover:underline"
                      >
                        <span>🎬 Fonte de Mídia / YouTube Oficial:</span>
                        <span className="truncate max-w-md">{log.repostUrl}</span>
                        <span>↗</span>
                      </a>
                    )}
                  </div>

                  {/* BOX DE RACIOCÍNIO DA IA */}
                  <div className="bg-slate-900/90 border border-indigo-500/20 rounded-xl p-4 relative">
                    <div className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <span>🧠</span> Raciocínio & Decisão Editorial da IA:
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed font-mono">
                      {log.reasoning}
                    </p>
                  </div>

                  {/* BOX DE CORREÇÕES APÓS TÉRMINO */}
                  {log.correctionsMade && log.correctionsMade !== 'Nenhuma correção necessária.' && (
                    <div className="bg-cyan-950/20 border border-cyan-500/20 rounded-xl p-3">
                      <div className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                        <span>🩺</span> Autocorreção & Auditoria de Qualidade:
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {log.correctionsMade}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
