'use client';
import React, { useEffect, useState } from 'react';

function Sparkline({ data, color, height = 50 }: { data: number[]; color: string; height?: number }) {
  if (!data || data.length < 2) return <div className="h-12 flex items-center justify-center text-slate-600 text-xs">Sem dados ainda</div>;
  const max = Math.max(...data, 1);
  const width = 400;
  const pad = 4;
  const step = (width - pad * 2) / (data.length - 1);
  const points = data.map((v, i) => `${pad + i * step},${height - pad - ((v / max) * (height - pad * 2))}`).join(' ');
  const areaPoints = `${pad},${height - pad} ${points} ${pad + (data.length - 1) * step},${height - pad}`;
  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`mg-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.02" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints} fill={`url(#mg-${color.replace('#','')})`} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function KioskPage() {
  const [data, setData] = useState<any>(null);
  const [blogId, setBlogId] = useState('global');
  const [loading, setLoading] = useState(true);

  // Busca dados a cada 60 segundos
  useEffect(() => {
    const saved = localStorage.getItem('apollo_active_workspace') || 'global';
    setBlogId(saved);
    fetchData(saved);
    const interval = setInterval(() => fetchData(saved), 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async (id: string) => {
    try {
      const res = await fetch(`/api/admin/stats?blogId=${id}`);
      const json = await res.json();
      if (json.success) setData(json.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  if (loading) return (
    <div className="flex items-center justify-center h-screen bg-black gap-4">
      <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  const postsData = data?.postsChart?.map((d: any) => d.count) || [];
  const leadsData = data?.leadsChart?.map((d: any) => d.count) || [];

  return (
    <div className="min-h-screen bg-black text-slate-200 p-8 font-sans overflow-hidden flex flex-col cursor-none">
      
      {/* Header Kiosk */}
      <div className="flex justify-between items-center mb-10 shrink-0">
        <div>
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-300 tracking-tight">
            AUTO-BLOG CMS <span className="text-slate-600 font-normal">|</span> {blogId.toUpperCase()}
          </h1>
          <p className="text-slate-400 text-lg mt-2 font-mono uppercase tracking-widest flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            Monitoramento em Tempo Real (Kiosk Mode)
          </p>
        </div>
        <div className="text-right">
          <p className="text-4xl font-mono text-slate-300 font-bold">{new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}</p>
          <p className="text-slate-500 font-mono text-sm">{new Date().toLocaleDateString('pt-BR')}</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="flex-1 grid grid-cols-12 gap-8 min-h-0">
        
        {/* Coluna Esquerda: KPIs (4 colunas) */}
        <div className="col-span-4 flex flex-col gap-8 h-full">
          <div className="bg-slate-900/80 rounded-3xl border border-slate-800 p-8 flex-1 flex flex-col justify-center relative overflow-hidden">
            <div className="absolute -right-12 -top-12 w-40 h-40 rounded-full blur-3xl opacity-20 bg-blue-500" />
            <p className="text-slate-400 font-bold text-sm tracking-widest uppercase mb-4">Total de Artigos</p>
            <div className="flex items-end gap-3">
              <span className="text-4xl">📝</span>
              <p className="text-7xl font-black text-white">{data?.totalPosts || 0}</p>
            </div>
          </div>
          
          <div className="bg-slate-900/80 rounded-3xl border border-slate-800 p-8 flex-1 flex flex-col justify-center relative overflow-hidden">
            <div className="absolute -right-12 -top-12 w-40 h-40 rounded-full blur-3xl opacity-20 bg-emerald-500" />
            <p className="text-slate-400 font-bold text-sm tracking-widest uppercase mb-4">Leads Capturados</p>
            <div className="flex items-end gap-3">
              <span className="text-4xl">📬</span>
              <p className="text-7xl font-black text-white">{data?.totalLeads || 0}</p>
            </div>
          </div>
        </div>

        {/* Coluna Direita: Gráficos (8 colunas) */}
        <div className="col-span-8 flex flex-col gap-8 h-full">
          <div className="bg-slate-900/80 rounded-3xl border border-slate-800 p-8 flex-1 flex flex-col relative overflow-hidden">
             <div className="absolute -left-12 -top-12 w-40 h-40 rounded-full blur-3xl opacity-10 bg-blue-500" />
             <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3"><span className="text-blue-400">📝</span> Produção Diária (14d)</h2>
             <div className="flex-1 flex items-center w-full min-h-[150px]">
               <Sparkline data={postsData} color="#3b82f6" height={150} />
             </div>
          </div>

          <div className="bg-slate-900/80 rounded-3xl border border-slate-800 p-8 flex-1 flex flex-col relative overflow-hidden">
             <div className="absolute -left-12 -top-12 w-40 h-40 rounded-full blur-3xl opacity-10 bg-emerald-500" />
             <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3"><span className="text-emerald-400">📬</span> Aquisição de Leads (14d)</h2>
             <div className="flex-1 flex items-center w-full min-h-[150px]">
               <Sparkline data={leadsData} color="#10b981" height={150} />
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
