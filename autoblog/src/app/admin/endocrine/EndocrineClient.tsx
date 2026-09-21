'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface EndocrineLog {
  id: string;
  blogId: string;
  blogName: string;
  actionType: 'hormone_homeostasis' | 'fact_checking' | 'viral_boost';
  details: string;
  hormoneBalance?: string;
  createdAt: string;
}

interface Stats {
  totalHomeostasis: number;
  totalFactChecks: number;
  totalViralBoosts: number;
  auditedPosts: number;
}

const ACTION_META: Record<string, { label: string; icon: string; color: string; border: string }> = {
  hormone_homeostasis: { label: 'HOMEOSTASE HORMONAL', icon: '⚖️', color: 'text-sky-300', border: 'border-sky-500/50' },
  fact_checking: { label: 'FACT-CHECKING NEURAL', icon: '🛡️', color: 'text-violet-300', border: 'border-violet-500/50' },
  viral_boost: { label: 'HORMÔNIO VIRAL TURBO', icon: '🔥', color: 'text-rose-300', border: 'border-rose-500/50' },
};

export default function EndocrineClient() {
  const [logs, setLogs] = useState<EndocrineLog[]>([]);
  const [stats, setStats] = useState<Stats>({ totalHomeostasis: 0, totalFactChecks: 0, totalViralBoosts: 0, auditedPosts: 0 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/admin/endocrine?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('[Endocrine] Erro ao buscar logs:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 15000);
    return () => clearInterval(interval);
  }, [selectedBlog]);

  const handleAction = async (action: string, label: string) => {
    setActionLoading(action);
    setToast({ message: `⏳ ${label}...`, type: 'info' });
    try {
      const res = await fetch('/api/admin/endocrine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog }),
      });
      const data = await res.json();
      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Ciclo endócrino executado com sucesso!'}`, type: 'success' });
        await fetchLogs();
      } else {
        setToast({ message: `❌ Erro: ${data.error}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro de rede: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const getMeta = (type: string) => ACTION_META[type] || { label: 'EVENTO ENDÓCRINO', icon: '⚗️', color: 'text-slate-300', border: 'border-slate-600' };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* HEADER */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-sky-950/60 to-slate-900 border border-sky-500/30 p-8 shadow-2xl shadow-sky-950/40">
        <div className="absolute top-0 right-0 -mt-16 -mr-16 w-80 h-80 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-16 -ml-16 w-80 h-80 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-sky-500/20 border border-sky-400/30 text-sky-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-sky-400 animate-ping" />
              FASE 136 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              ⚗️ Sistema Endócrino & Fact-Checking
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              O glândula reguladora do organismo autônomo. Equilibra os hormônios editoriais do acervo (Adrenalina / Dopamina / Ocitocina), blinda matérias contra alucinações de IA com Selo de Autoridade e injeta Boost Viral em Threads para o X (Twitter).
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleAction('force_full_endocrine', 'Ativando todos os sistemas endócrinos da Colmeia')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-sky-600 to-violet-600 hover:from-sky-500 hover:to-violet-500 text-white font-bold rounded-2xl shadow-lg shadow-sky-600/30 transition-all transform hover:-translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
            >
              {actionLoading === 'force_full_endocrine' ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span>⚗️</span>}
              <span>Forçar Ciclo Endócrino Agora</span>
            </button>
            <button onClick={() => handleAction('force_homeostasis', 'Medindo Balanço Hormonal Editorial')} disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-sky-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>⚖️</span> Homeostase
            </button>
            <button onClick={() => handleAction('force_factcheck', 'Executando Fact-Checking Anti-Alucinação')} disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-violet-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>🛡️</span> Fact-Check
            </button>
            <button onClick={() => handleAction('force_viralboost', 'Injetando Hormônio Viral em matérias')} disabled={actionLoading !== null}
              className="px-4 py-3 bg-slate-800/80 hover:bg-slate-800 border border-slate-700 hover:border-rose-500/50 text-slate-200 font-bold rounded-2xl transition-all flex items-center gap-2 disabled:opacity-50 text-sm">
              <span>🔥</span> Boost Viral
            </button>
          </div>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '⚖️ Homeostases Aplicadas', value: stats.totalHomeostasis, color: 'text-sky-400', border: 'hover:border-sky-500/50', sub: 'Pautas reequilibradas' },
          { label: '🛡️ Fact-Checks Realizados', value: stats.totalFactChecks, color: 'text-violet-400', border: 'hover:border-violet-500/50', sub: 'Blindagens anti-alucinação' },
          { label: '🔥 Boosts Virais Injetados', value: stats.totalViralBoosts, color: 'text-rose-400', border: 'hover:border-rose-500/50', sub: 'Threads X (Twitter) geradas' },
          { label: '✅ Artigos c/ Selo IA', value: stats.auditedPosts, color: 'text-emerald-400', border: 'hover:border-emerald-500/50', sub: '[✔ Auditado por IA]' },
        ].map((s) => (
          <div key={s.label} className={`bg-slate-900/80 border border-slate-800 rounded-2xl p-5 transition-all ${s.border}`}>
            <div className="text-slate-400 text-xs font-bold uppercase tracking-wider">{s.label}</div>
            <div className={`text-3xl font-black mt-2 ${s.color}`}>{s.value}</div>
            <div className="text-xs text-slate-500 mt-1">{s.sub}</div>
          </div>
        ))}
      </div>

      {/* FILTRO */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50 border border-slate-800 p-4 rounded-2xl">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Portal:</label>
          <select value={selectedBlog} onChange={(e) => setSelectedBlog(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-sky-500 transition-all font-medium">
            <option value="all">🌐 Todos os Portais</option>
            <option value="descarga">📥 Descarga News</option>
            <option value="darktrap">🎵 Dark Trap Radio</option>
            <option value="macaco">🐒 Macaco Driver</option>
          </select>
        </div>
        <button onClick={() => handleAction('clear_logs', 'Limpando telemetria endócrina')} disabled={actionLoading !== null || logs.length === 0}
          className="text-xs text-slate-500 hover:text-red-400 transition-colors font-semibold flex items-center gap-1.5 disabled:opacity-30">
          <span>🧹</span> Limpar Telemetria
        </button>
      </div>

      {/* FEED */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>🧪</span> Registro de Intervenções Endócrinas
        </h2>

        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm font-medium">Sincronizando sistema hormonal...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <div className="text-4xl mb-3">⚗️</div>
            <h3 className="text-lg font-bold text-slate-300">Nenhuma intervenção endócrina registrada ainda!</h3>
            <p className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
              Clique em &quot;Forçar Ciclo Endócrino Agora&quot; para executar a homeostase hormonal, fact-checking e boost viral do acervo.
            </p>
          </div>
        ) : (
          <div className="space-y-5">
            {logs.map((log) => {
              const meta = getMeta(log.actionType);
              return (
                <div key={log.id} className={`bg-slate-950/80 border border-slate-800/80 hover:border-slate-700 rounded-2xl p-6 transition-all`}>
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-4 border-b border-slate-800/60">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className={`bg-slate-900/80 border ${meta.border} ${meta.color} px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider`}>
                        {meta.icon} {meta.label}
                      </span>
                      <span className="bg-slate-800 text-sky-300 px-3 py-1 rounded-lg text-xs font-bold">🏛️ {log.blogName}</span>
                      {log.hormoneBalance && (
                        <span className="bg-slate-900 border border-slate-800 text-slate-400 px-3 py-1 rounded-lg text-xs font-mono">{log.hormoneBalance}</span>
                      )}
                    </div>
                    <span className="text-slate-500 text-xs font-mono">🕒 {log.createdAt}</span>
                  </div>
                  <div className="bg-slate-900/90 border border-sky-500/20 rounded-xl p-4">
                    <div className="text-xs font-bold text-sky-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                      <span>⚗️</span> Relatório de Intervenção:
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed font-mono">{log.details}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
