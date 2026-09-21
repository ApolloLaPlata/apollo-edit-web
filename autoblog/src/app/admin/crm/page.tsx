'use client';

import React, { useState, useEffect } from 'react';

export default function CRMAdminPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState<{ message: string, type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const blogId = localStorage.getItem('apollo_active_workspace') || 'global';
      const res = await fetch(`/api/admin/crm?blogId=${blogId}`);
      const data = await res.json();
      if (data.success) {
        setLeads(data.leads || []);
        setStats(data.stats);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    try {
      const res = await fetch('/api/admin/crm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'seed' })
      });
      if (res.ok) {
        setToast({ message: 'Leads de teste injetados!', type: 'success' });
        fetchData();
      }
    } catch (e) {}
    setTimeout(() => setToast(null), 3000);
  };

  const handleFireNewsletter = () => {
    setToast({ message: 'Disparando crm_mailer.js no background...', type: 'success' });
    setTimeout(() => setToast(null), 3000);
  };

  return (
    <div className="max-w-[1440px] mx-auto space-y-10 pb-16 animate-in fade-in duration-500 relative">
      
      {/* Toast Notification */}
      {toast && (
        <div className={`fixed bottom-6 right-6 px-6 py-3 rounded-xl shadow-2xl font-bold text-sm z-50 animate-in slide-in-from-right-10 flex items-center gap-3 ${toast.type === 'success' ? 'bg-emerald-500/90 text-white' : 'bg-red-500/90 text-white'}`}>
           {toast.type === 'success' ? '✓' : '⚠'} {toast.message}
        </div>
      )}

      {/* Header Glassmorphism */}
      <div className="bg-gradient-to-br from-indigo-900/40 via-purple-900/30 to-slate-900/40 backdrop-blur-3xl p-10 rounded-3xl border border-indigo-500/30 shadow-[0_0_50px_rgba(99,102,241,0.1)] relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/20 rounded-full blur-[100px] pointer-events-none -mr-40 -mt-40 animate-pulse" />
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-[10px] font-black uppercase tracking-widest mb-4 shadow-[0_0_10px_rgba(99,102,241,0.2)]">
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping" />
              CRM & Email Marketing
            </div>
            <h1 className="text-4xl font-black text-white tracking-tight mb-2">Base de Leads & Retenção</h1>
            <p className="text-slate-400 font-medium max-w-xl">Gerencie os usuários capturados pelo Paywall. Exporte os dados ou dispare Newsletters premium.</p>
          </div>
          <div className="flex gap-4">
            <button 
              onClick={handleSeed}
              className="bg-slate-800/80 hover:bg-slate-700 text-white font-bold px-5 py-2.5 rounded-xl border border-slate-600 transition-all shadow-lg text-sm"
            >
              Popular Dados (Mock)
            </button>
            <button 
              onClick={handleFireNewsletter}
              className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold px-6 py-2.5 rounded-xl border border-indigo-500/50 transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)] flex items-center gap-2"
            >
              ▶ Disparar Newsletter VIP
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
           <div className="h-32 bg-slate-800/40 animate-pulse rounded-2xl border border-slate-800"></div>
           <div className="h-32 bg-slate-800/40 animate-pulse rounded-2xl border border-slate-800"></div>
           <div className="h-32 bg-slate-800/40 animate-pulse rounded-2xl border border-slate-800"></div>
           <div className="h-32 bg-slate-800/40 animate-pulse rounded-2xl border border-slate-800"></div>
        </div>
      ) : (
        <>
          {/* Métricas do CRM */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
             <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Total de Leads</div>
                <div className="text-4xl font-black text-white font-mono">{stats?.total.toLocaleString()}</div>
             </div>
             
             <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-emerald-900/50 shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl" />
                <div className="text-xs font-bold uppercase tracking-wider text-emerald-500/70 mb-4 relative z-10">Leads Ativos (Engajados)</div>
                <div className="text-4xl font-black text-emerald-400 font-mono relative z-10">{stats?.active.toLocaleString()}</div>
             </div>
             
             <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">Novos Leads (Hoje)</div>
                <div className="text-4xl font-black text-cyan-400 font-mono">+{stats?.today}</div>
             </div>
             
             <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-rose-900/30 shadow-xl relative overflow-hidden">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-4">Bounces / Unsubscribes</div>
                <div className="text-4xl font-black text-slate-500 font-mono">{stats?.bounced}</div>
             </div>
          </div>

          {/* Tabela de Leads */}
          <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-950/40">
               <div>
                 <h2 className="text-lg font-bold text-white flex items-center gap-2">
                   <span className="text-indigo-400">📋</span> Registro de Audiência Capturada
                 </h2>
                 <p className="text-xs text-slate-500 mt-1">Exibindo os últimos 100 leads cadastrados pelo Paywall.</p>
               </div>
               
               <button className="text-xs font-bold px-4 py-2 rounded-lg border border-slate-700 hover:bg-slate-800 text-slate-300 transition-colors">
                 ↓ Exportar CSV
               </button>
            </div>
            
            <div className="overflow-x-auto">
               <table className="w-full text-left">
                 <thead>
                   <tr className="border-b border-slate-800 text-[10px] uppercase tracking-widest text-slate-500 bg-slate-900/50">
                     <th className="px-6 py-4">Lead ID</th>
                     <th className="px-6 py-4">E-mail Cadastrado</th>
                     <th className="px-6 py-4">Origem / Blog</th>
                     <th className="px-6 py-4">Score</th>
                     <th className="px-6 py-4 text-right">Ação</th>
                   </tr>
                 </thead>
                 <tbody className="divide-y divide-slate-800/50 text-sm text-slate-300">
                   {leads.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-slate-500 italic">
                           Nenhum lead capturado ainda. O tráfego precisa bater na Paywall.
                        </td>
                      </tr>
                   ) : (
                      leads.map((lead) => (
                        <tr key={lead.id} className="hover:bg-slate-800/30 transition-colors group">
                           <td className="px-6 py-4 font-mono text-[11px] text-slate-500">{lead.id.substring(0,8)}...</td>
                           <td className="px-6 py-4 font-bold text-white group-hover:text-indigo-400 transition-colors">{lead.email}</td>
                           <td className="px-6 py-4 text-xs">
                             <span className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700">
                               {lead.blogName || lead.blogId.substring(0,12)}
                             </span>
                           </td>
                           <td className="px-6 py-4">
                              <div className="flex items-center gap-2">
                                <span className="text-amber-400">🔥</span>
                                <span className="font-mono font-bold text-slate-300">{lead.opens || 0}</span>
                              </div>
                           </td>
                           <td className="px-6 py-4 text-right">
                              <button className="text-xs text-rose-500 hover:text-rose-400 font-bold px-3 py-1 rounded border border-rose-500/20 hover:bg-rose-500/10 transition-colors">
                                Bloquear
                              </button>
                           </td>
                        </tr>
                      ))
                   )}
                 </tbody>
               </table>
            </div>
          </div>
        </>
      )}

    </div>
  );
}
