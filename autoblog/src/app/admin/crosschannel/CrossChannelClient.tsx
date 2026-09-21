'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Toast from '@/components/ui/Toast';

interface PlatformData {
  impressions: number;
  clicks: number;
  engagement: number;
  delta: number;
  trend: 'up' | 'down' | 'stable';
}

interface Insight {
  id: string;
  blogId: string;
  summary: string;
  recommendation: string;
  priorityPlatform: string;
  createdAt: string;
}

interface Totals {
  impressions: number;
  clicks: number;
  engagement: number;
  ctr: string;
}

const PLATFORM_META: Record<string, { label: string; icon: string; bg: string; border: string; text: string }> = {
  youtube:   { label: 'YouTube',   icon: '🎬', bg: 'from-red-950/60 to-slate-900',    border: 'border-red-500/40',    text: 'text-red-400' },
  twitter:   { label: 'X (Twitter)', icon: '🐦', bg: 'from-slate-800/80 to-slate-900',  border: 'border-slate-500/40',  text: 'text-slate-300' },
  instagram: { label: 'Instagram', icon: '📸', bg: 'from-pink-950/60 to-slate-900',   border: 'border-pink-500/40',   text: 'text-pink-400' },
  telegram:  { label: 'Telegram',  icon: '📨', bg: 'from-sky-950/60 to-slate-900',    border: 'border-sky-500/40',    text: 'text-sky-400' },
  tiktok:    { label: 'TikTok',    icon: '🎵', bg: 'from-purple-950/60 to-slate-900', border: 'border-purple-500/40', text: 'text-purple-400' },
  facebook:  { label: 'Facebook',  icon: '📘', bg: 'from-blue-950/60 to-slate-900',   border: 'border-blue-500/40',   text: 'text-blue-400' },
  linkedin:  { label: 'LinkedIn',  icon: '💼', bg: 'from-indigo-950/60 to-slate-900', border: 'border-indigo-500/40', text: 'text-indigo-400' },
  google:    { label: 'Google',    icon: '🔍', bg: 'from-emerald-950/60 to-slate-900',border: 'border-emerald-500/40',text: 'text-emerald-400' },
};

const PLATFORM_ORDER = ['google', 'youtube', 'tiktok', 'instagram', 'twitter', 'telegram', 'facebook', 'linkedin'];

function fmt(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M';
  if (n >= 1_000)     return (n / 1_000).toFixed(1) + 'K';
  return String(n);
}

export default function CrossChannelClient() {
  const [platformData, setPlatformData] = useState<Record<string, PlatformData>>({});
  const [insights, setInsights] = useState<Insight[]>([]);
  const [totals, setTotals] = useState<Totals>({ impressions: 0, clicks: 0, engagement: 0, ctr: '0.00' });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const res = await fetch(`/api/admin/crosschannel?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setPlatformData(data.platformData || {});
        setInsights(data.insights || []);
        setTotals(data.totals || { impressions: 0, clicks: 0, engagement: 0, ctr: '0.00' });
      }
    } catch (e) {
      console.error('[CrossChannel] Erro ao buscar telemetria:', e);
    } finally {
      setLoading(false);
    }
  }, [selectedBlog]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 20000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleAction = async (action: string, label: string) => {
    setActionLoading(action);
    setToast({ message: `📡 ${label}...`, type: 'info' });
    try {
      const res = await fetch('/api/admin/crosschannel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog }),
      });
      const data = await res.json();
      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Telemetria atualizada!'}`, type: 'success' });
        await fetchData();
      } else {
        setToast({ message: `❌ Erro: ${data.error}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const noData = Object.keys(platformData).length === 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* ── HEADER ── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-rose-950/40 to-slate-900 border border-rose-500/30 p-8 shadow-2xl shadow-rose-950/30">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-rose-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-rose-500/20 border border-rose-400/30 text-rose-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
              FASE 137 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              📡 Telemetria Cross-Channel
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              Cockpit executivo de tráfego orgânico consolidado em tempo real: 8 redes sociais monitoradas simultaneamente. O Qwen 72B analisa os dados e gera recomendações estratégicas para maximizar o alcance da Colmeia.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button onClick={() => handleAction('force_full_scan', 'Executando varredura total de 8 canais')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-rose-600 to-orange-600 hover:from-rose-500 hover:to-orange-500 text-white font-bold rounded-2xl shadow-lg shadow-rose-600/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center gap-2">
              {actionLoading === 'force_full_scan' ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span>📡</span>}
              <span>Varredura Total Agora</span>
            </button>
            <button onClick={() => handleAction('force_radar', 'Atualizando radar de métricas')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-rose-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>📊</span> Radar
            </button>
            <button onClick={() => handleAction('force_intelligence', 'Gerando insights estratégicos com IA')}
              disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-orange-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>🧠</span> Analisar
            </button>
          </div>
        </div>
      </div>

      {/* ── KPIs GLOBAIS ── */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '👁️ Impressões Totais', value: fmt(totals.impressions), sub: 'Todas as 8 redes', color: 'text-rose-400', border: 'hover:border-rose-500/50' },
          { label: '🖱️ Cliques Orgânicos', value: fmt(totals.clicks), sub: 'Tráfego direto gerado', color: 'text-orange-400', border: 'hover:border-orange-500/50' },
          { label: '💬 Engajamento Total', value: fmt(totals.engagement), sub: 'Reações + comentários', color: 'text-amber-400', border: 'hover:border-amber-500/50' },
          { label: '📈 CTR Médio Global', value: `${totals.ctr}%`, sub: 'Click-through rate', color: 'text-emerald-400', border: 'hover:border-emerald-500/50' },
        ].map((kpi) => (
          <div key={kpi.label} className={`bg-slate-900/80 border border-slate-800 rounded-2xl p-5 transition-all ${kpi.border}`}>
            <div className="text-slate-400 text-xs font-bold uppercase tracking-wider leading-tight">{kpi.label}</div>
            <div className={`text-3xl font-black mt-2 ${kpi.color}`}>{loading ? '…' : kpi.value}</div>
            <div className="text-xs text-slate-500 mt-1">{kpi.sub}</div>
          </div>
        ))}
      </div>

      {/* ── FILTRO ── */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50 border border-slate-800 p-4 rounded-2xl">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Portal:</label>
          <select value={selectedBlog} onChange={(e) => setSelectedBlog(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-rose-500 transition-all font-medium">
            <option value="all">🌐 Todos os Portais</option>
            <option value="descarga">📥 Descarga News</option>
            <option value="darktrap">🎵 Dark Trap Radio</option>
            <option value="macaco">🐒 Macaco Driver</option>
          </select>
        </div>
        <button onClick={() => handleAction('clear_metrics', 'Limpando métricas acumuladas')}
          disabled={actionLoading !== null || noData}
          className="text-xs text-slate-500 hover:text-red-400 transition-colors font-semibold flex items-center gap-1.5 disabled:opacity-30">
          <span>🧹</span> Limpar Telemetria
        </button>
      </div>

      {/* ── GRID DE 8 PLATAFORMAS ── */}
      {loading ? (
        <div className="py-20 text-center text-slate-500">
          <div className="w-10 h-10 border-4 border-rose-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm font-medium">Sincronizando radar de 8 canais...</p>
        </div>
      ) : noData ? (
        <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
          <div className="text-4xl mb-3">📡</div>
          <h3 className="text-lg font-bold text-slate-300">Nenhuma métrica coletada ainda!</h3>
          <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">Clique em &quot;Varredura Total Agora&quot; para iniciar o Radar de 8 canais e popular o cockpit.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PLATFORM_ORDER.map((platform) => {
            const meta = PLATFORM_META[platform];
            const d = platformData[platform] || { impressions: 0, clicks: 0, engagement: 0, delta: 0, trend: 'stable' };
            const trendIcon = d.trend === 'up' ? '↑' : d.trend === 'down' ? '↓' : '→';
            const trendColor = d.trend === 'up' ? 'text-emerald-400' : d.trend === 'down' ? 'text-red-400' : 'text-slate-400';
            return (
              <div key={platform} className={`bg-gradient-to-b ${meta.bg} border ${meta.border} rounded-2xl p-5 transition-all hover:scale-[1.02] hover:shadow-lg`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl">{meta.icon}</span>
                    <span className={`font-bold text-sm ${meta.text}`}>{meta.label}</span>
                  </div>
                  <span className={`text-xs font-bold ${trendColor} bg-slate-900/60 px-2 py-0.5 rounded-full`}>{trendIcon} {d.trend}</span>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500">Impressões</span>
                    <span className={`text-sm font-bold ${meta.text}`}>{fmt(d.impressions)}</span>
                  </div>
                  <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                    <div className={`h-full bg-current ${meta.text} opacity-60 transition-all duration-1000`}
                      style={{ width: `${Math.min(100, (d.impressions / 50000) * 100)}%` }} />
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500">Cliques</span>
                    <span className="text-sm font-semibold text-slate-300">{fmt(d.clicks)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-500">Engajamento</span>
                    <span className="text-sm font-semibold text-slate-300">{fmt(d.engagement)}</span>
                  </div>
                  {d.impressions > 0 && (
                    <div className="flex justify-between items-center pt-1 border-t border-slate-800/60">
                      <span className="text-xs text-slate-500">CTR</span>
                      <span className="text-xs font-bold text-emerald-400">
                        {((d.clicks / d.impressions) * 100).toFixed(1)}%
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ── INSIGHTS ESTRATÉGICOS DA IA ── */}
      {insights.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <span>🧠</span> Inteligência Estratégica Cross-Channel (Análises do Qwen 72B)
          </h2>
          <div className="space-y-5">
            {insights.map((insight) => (
              <div key={insight.id} className="bg-slate-950/80 border border-rose-500/20 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-800/60">
                  <span className="bg-rose-950 border border-rose-500/40 text-rose-300 px-3 py-1 rounded-full text-xs font-bold uppercase">
                    🎯 PRIORIDADE: {insight.priorityPlatform?.toUpperCase()}
                  </span>
                  <span className="text-slate-500 text-xs font-mono">🕒 {insight.createdAt}</span>
                </div>
                <p className="text-slate-200 text-sm leading-relaxed mb-3">
                  <span className="text-rose-400 font-bold">📊 Análise: </span>{insight.summary}
                </p>
                <div className="bg-slate-900/80 border border-emerald-500/20 rounded-xl p-4">
                  <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-1">🚀 Ação Recomendada pela IA:</div>
                  <p className="text-sm text-slate-300 font-mono">{insight.recommendation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
