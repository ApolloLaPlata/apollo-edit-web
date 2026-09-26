'use client';

import React, { useEffect, useState } from 'react';
import Toast from '@/components/ui/Toast';

interface SeoHealerLog {
  id: string;
  blogId: string;
  blogName: string;
  postId: string;
  postTitle: string;
  actionType: 'meta_optimization' | 'keyword_density' | 'schema_injection';
  details: string;
  createdAt: string;
}

interface Stats {
  pending: number;
  healed: number;
  totalHeals: number;
}

export default function SeoHealerClient() {
  const [logs, setLogs] = useState<SeoHealerLog[]>([]);
  const [stats, setStats] = useState<Stats>({ pending: 0, healed: 0, totalHeals: 0 });
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' | 'info' } | null>(null);

  const fetchLogs = async () => {
    try {
      const res = await fetch(`/api/admin/seohealer?blogId=${selectedBlog}`);
      const data = await res.json();
      if (data.success) {
        setLogs(data.logs || []);
        if (data.stats) setStats(data.stats);
      }
    } catch (e) {
      console.error('[SeoHealer] Erro:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 20000);
    return () => clearInterval(interval);
  }, [selectedBlog]);

  const handleAction = async (action: string, label: string) => {
    setActionLoading(action);
    setToast({ message: `🛠️ ${label}...`, type: 'info' });
    try {
      const res = await fetch('/api/admin/seohealer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, blogId: selectedBlog === 'all' ? 'global' : selectedBlog }),
      });
      const data = await res.json();
      if (data.success) {
        setToast({ message: `✅ ${data.message || 'Ciclo de auto-cura concluído!'}`, type: 'success' });
        await fetchLogs();
      } else {
        setToast({ message: `❌ Erro: ${data.error}`, type: 'error' });
      }
    } catch (e: any) {
      setToast({ message: `❌ Erro: ${e.message}`, type: 'error' });
    } finally {
      setActionLoading(null);
    }
  };

  const coverage = stats.pending + stats.healed > 0 
    ? Math.round((stats.healed / (stats.pending + stats.healed)) * 100) 
    : 100;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16 animate-fadeIn">
      {toast && <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />}

      {/* HEADER */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-teal-950/40 to-slate-900 border border-teal-500/30 p-8 shadow-2xl shadow-teal-950/30">
        <div className="absolute top-0 right-0 -mt-24 -mr-24 w-96 h-96 bg-teal-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-24 -ml-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-teal-500/20 border border-teal-400/30 text-teal-300 text-xs font-bold uppercase tracking-widest mb-3">
              <span className="w-2 h-2 rounded-full bg-teal-400 animate-ping" />
              FASE 139 · PROTOCOLO COLMEIA
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-white flex items-center gap-3">
              🛠️ Auto-Healer SEO On-Page
            </h1>
            <p className="text-slate-300 mt-2 text-sm md:text-base max-w-2xl leading-relaxed">
              O zelador autônomo da infraestrutura. Ele varre silenciosamente o acervo, detectando falhas de SEO e injetando Meta Tags, Densidade de Keywords e Schema.org JSON-LD para agradar o algoritmo do Google.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button onClick={() => handleAction('force_full_heal', 'Varrendo e Curando Acervo')}
              disabled={actionLoading !== null}
              className="px-6 py-3 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white font-bold rounded-2xl shadow-lg shadow-teal-600/30 transition-all transform hover:-translate-y-0.5 flex items-center gap-2 disabled:opacity-50">
              {actionLoading === 'force_full_heal' ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span>🛠️</span>}
              Forçar Cura de SEO Agora
            </button>
          </div>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '🛡️ Cobertura SEO', value: `${coverage}%`, color: coverage === 100 ? 'text-emerald-400' : 'text-amber-400' },
          { label: '✅ Matérias Curadas', value: stats.healed, color: 'text-teal-400' },
          { label: '⚠️ Curas Pendentes', value: stats.pending, color: stats.pending > 0 ? 'text-rose-400' : 'text-slate-500' },
          { label: '💉 Total de Injeções', value: stats.totalHeals, color: 'text-emerald-400' },
        ].map(s => (
          <div key={s.label} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5">
            <div className="text-slate-400 text-xs font-bold uppercase">{s.label}</div>
            <div className={`text-3xl font-black mt-2 ${s.color}`}>{loading ? '…' : s.value}</div>
          </div>
        ))}
      </div>

      {/* FILTRO */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 bg-slate-900/50 border border-slate-800 p-4 rounded-2xl">
        <div className="flex items-center gap-3">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-400">Portal:</label>
          <select value={selectedBlog} onChange={(e) => setSelectedBlog(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-xl px-4 py-2 focus:outline-none focus:border-teal-500 transition-all font-medium">
            <option value="all">🌐 Todos os Portais</option>
            <option value="descarga">📥 Descarga News</option>
            <option value="darktrap">🎵 Dark Trap Radio</option>
            <option value="macaco">🐒 Macaco Driver</option>
          </select>
        </div>
        <button onClick={() => handleAction('clear_logs', 'Limpando logs de cura')}
          disabled={actionLoading !== null || logs.length === 0}
          className="text-xs text-slate-500 hover:text-red-400 transition-colors font-semibold flex items-center gap-1.5 disabled:opacity-30">
          <span>🧹</span> Limpar Registros
        </button>
      </div>

      {/* FEED DE LOGS */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 md:p-8 shadow-xl">
        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <span>📋</span> Registro de Intervenções (Meta & Schema.org)
        </h2>
        {loading ? (
          <div className="py-20 text-center text-slate-500">
            <div className="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
            <p className="text-sm">Varrendo histórico de curas...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="py-20 text-center bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <div className="text-4xl mb-3">🛠️</div>
            <h3 className="text-lg font-bold text-slate-300">Ainda não houve intervenções do Auto-Healer</h3>
            <p className="text-sm text-slate-500 mt-1">Quando matérias sem metadados forem detectadas, os robôs irão curá-las automaticamente e registrarão aqui.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {logs.map(log => (
              <div key={log.id} className="bg-slate-950/80 border border-teal-500/20 hover:border-teal-500/40 rounded-2xl p-5 transition-all">
                <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
                  <div className="flex items-center gap-3">
                    <span className="bg-teal-950 text-teal-400 border border-teal-500/30 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1">
                      <span>💉</span> {log.actionType.replace('_', ' ')}
                    </span>
                    <span className="bg-slate-800 text-slate-300 px-3 py-1 rounded-lg text-xs font-bold">{log.blogName}</span>
                  </div>
                  <span className="text-slate-500 text-xs font-mono">{log.createdAt}</span>
                </div>
                <h4 className="text-lg font-bold text-slate-200 mb-2">{log.postTitle}</h4>
                <div className="bg-slate-900 rounded-xl p-3 border border-slate-800 text-sm font-mono text-slate-400">
                  <span className="text-emerald-400 font-bold">Diagnóstico & Cura: </span>
                  {log.details}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
