'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface TrendForecast {
  id: string;
  blogId: string;
  blogName: string;
  topic: string;
  category: string;
  confidenceScore: number;
  trendWindow: '6h' | '12h' | '24h' | '48h';
  reasoning: string;
  scheduledFor: string;
  status: 'queued' | 'published' | 'expired';
  createdAt: string;
}

interface Stats {
  queued: number;
  published: number;
  expired: number;
}

export default function TrendClient() {
  const [forecasts, setForecasts] = useState<TrendForecast[]>([]);
  const [stats, setStats] = useState<Stats>({ queued: 0, published: 0, expired: 0 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchForecasts = async () => {
    try {
      const res = await fetch(`/api/admin/trend?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setForecasts(data.forecasts || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('[Trend] Erro ao buscar previsões:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecasts();
    const interval = setInterval(fetchForecasts, 20000);
    return () => clearInterval(interval);
  }, [selectedBlog]);

  const handleAction = async (action: string, label: string) => {
    setActionLoading(action);
    setToast({ message: `🔮 ${label}...`, type: 'info' });
    try {
      const res = await fetch('/api/admin/trend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog }),
      });
      const data = await res.json();
      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Ciclo de predição concluído!'}`, type: 'success' });
        await fetchForecasts();
      } else {
        setToast({ message: `❌ Erro: ${data.error}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* HEADER */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-purple-950/40 to-slate-900 border border-purple-500/30 p-8 shadow-2xl shadow-purple-950/30">
        <div className="absolute top-0 right-0 -mt-24 -mr-24 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-24 -ml-24 w-96 h-96 bg-fuchsia-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-purple-500/20 border border-purple-400/30 text-purple-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
              FASE 138 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              🔮 Oráculo de Tendências
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              O modelo neural prevê pautas virais analisando a telemetria cross-channel e o histórico do acervo. Assuntos são agendados e redigidos autonomamente antes mesmo de explodirem na internet.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button onClick={() => handleAction('force_full_trend', 'Ativando Oráculo de Predição')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-500 hover:to-fuchsia-500 text-white font-bold rounded-2xl shadow-lg shadow-purple-600/30 transition-all transform hover:-translate-y-0.5 flex items-center gap-2 disabled:opacity-50">
              {actionLoading === 'force_full_trend' ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span>🔮</span>}
              Consultar Oráculo
            </button>
            <button onClick={() => handleAction('force_dispatch', 'Disparando pautas agendadas')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-emerald-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>🚀</span> Disparar Fila
            </button>
          </div>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: '⏳ Pautas Agendadas', value: stats.queued, color: 'text-amber-400', border: 'border-amber-500/30' },
          { label: '✅ Pautas Publicadas', value: stats.published, color: 'text-emerald-400', border: 'border-emerald-500/30' },
          { label: '🗑️ Pautas Expiradas', value: stats.expired, color: 'text-slate-500', border: 'border-slate-500/30' },
        ].map(s => (
          <div key={s.label} className={`bg-slate-900/80 border ${s.border} rounded-2xl p-5 text-center`}>
            <div className="text-slate-400 text-xs font-bold uppercase">{s.label}</div>
            <div className={`text-4xl font-black mt-2 ${s.color}`}>{loading ? '…' : s.value}</div>
          </div>
        ))}
      </div>

      {/* FILTRO E LISTA */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50 border border-slate-800 p-4 rounded-2xl">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Portal:</label>
          <select value={selectedBlog} onChange={(e) => setSelectedBlog(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-purple-500 transition-all font-medium">
            <option value="all">🌐 Todos os Portais</option>
            <option value="descarga">📥 Descarga News</option>
            <option value="darktrap">🎵 Dark Trap Radio</option>
            <option value="macaco">🐒 Macaco Driver</option>
          </select>
        </div>
        <button onClick={() => handleAction('clear_expired', 'Limpando previsões antigas')}
          disabled={actionLoading !== null || stats.expired === 0}
          className="text-xs text-slate-500 hover:text-red-400 transition-colors font-semibold flex items-center gap-1.5 disabled:opacity-30">
          <span>🧹</span> Limpar Expiradas
        </button>
      </div>

      {/* GRID DE CARTÕES PREDITIVOS */}
      {loading ? (
        <div className="py-20 text-center text-slate-500">
          <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm">Sintonizando frequências preditivas...</p>
        </div>
      ) : forecasts.length === 0 ? (
        <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
          <div className="text-4xl mb-3">🔮</div>
          <h3 className="text-lg font-bold text-slate-300">A linha temporal está vazia</h3>
          <p className="text-sm text-slate-500 mt-1">Clique em "Consultar Oráculo" para prever os próximos hypes e agendar pautas automáticas.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {forecasts.map(f => {
            const isQueued = f.status === 'queued';
            const isPublished = f.status === 'published';
            const isExpired = f.status === 'expired';
            return (
              <div key={f.id} className={`relative overflow-hidden border rounded-3xl p-6 transition-all ${isQueued ? 'bg-slate-900/80 border-purple-500/30 hover:border-purple-500/60 shadow-lg shadow-purple-900/10' : isPublished ? 'bg-slate-900/40 border-emerald-500/20 opacity-80' : 'bg-slate-950 border-slate-800 opacity-60'}`}>
                {/* Score badge */}
                <div className="absolute top-6 right-6">
                  <div className={`px-3 py-1 rounded-full text-xs font-black border flex items-center gap-1 ${isQueued ? 'bg-purple-950 border-purple-500 text-purple-300' : isPublished ? 'bg-emerald-950 border-emerald-500 text-emerald-300' : 'bg-slate-900 border-slate-700 text-slate-400'}`}>
                    <span>🎯</span> {f.confidenceScore}/10
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="bg-slate-800 text-slate-300 px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wider">{f.blogName}</span>
                  <span className="bg-sky-950/50 text-sky-400 border border-sky-500/30 px-2.5 py-1 rounded-lg text-xs font-bold">{f.category}</span>
                  <span className="bg-amber-950/50 text-amber-400 border border-amber-500/30 px-2.5 py-1 rounded-lg text-xs font-bold flex items-center gap-1">⏱️ {f.trendWindow}</span>
                </div>

                <h3 className={`text-xl font-bold mb-3 leading-tight ${isExpired ? 'text-slate-500' : 'text-white'}`}>
                  {f.topic}
                </h3>

                <div className={`p-4 rounded-xl text-sm mb-5 font-mono ${isQueued ? 'bg-purple-950/20 text-purple-200 border border-purple-500/10' : 'bg-slate-950 text-slate-400'}`}>
                  <span className="font-bold uppercase tracking-wider text-xs mb-1 block opacity-70">Motivo da Previsão:</span>
                  {f.reasoning}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-800/60">
                  <div className="text-xs text-slate-400 flex items-center gap-2">
                    <span>🗓️ Agendado para:</span>
                    <span className="font-bold text-slate-200">{new Date(f.scheduledFor).toLocaleString()}</span>
                  </div>
                  {isQueued && <span className="text-xs font-bold text-amber-400 animate-pulse flex items-center gap-1"><span>⏳</span> Na fila de redação</span>}
                  {isPublished && <span className="text-xs font-bold text-emerald-400 flex items-center gap-1"><span>✅</span> Redigido e Publicado</span>}
                  {isExpired && <span className="text-xs font-bold text-slate-500">Expirou</span>}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
