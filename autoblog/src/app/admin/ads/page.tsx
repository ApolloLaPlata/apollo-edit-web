'use client';
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

export default function AdsManagerPage() {
  const [blogId, setBlogId] = useState('global');
  const [ads, setAds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form states
  const [inArticle, setInArticle] = useState({ code: '', isActive: true });
  const [stickyMobile, setStickyMobile] = useState({ code: '', isActive: true });
  const [horizontal, setHorizontal] = useState({ code: '', isActive: true });
  const [sidebar, setSidebar] = useState({ code: '', isActive: true });

  useEffect(() => {
    const saved = localStorage.getItem('apollo_active_workspace') || 'global';
    setBlogId(saved);
    fetchAds(saved);
  }, []);

  const fetchAds = async (id: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/ads?blogId=${id}`);
      const json = await res.json();
      if (json.success) {
        setAds(json.ads);
        // Pre-fill forms
        const ia = json.ads.find((a: any) => a.type === 'in_article');
        if (ia) setInArticle({ code: ia.code, isActive: Boolean(ia.isActive) });

        const sm = json.ads.find((a: any) => a.type === 'sticky_mobile');
        if (sm) setStickyMobile({ code: sm.code, isActive: Boolean(sm.isActive) });

        const hz = json.ads.find((a: any) => a.type === 'horizontal');
        if (hz) setHorizontal({ code: hz.code, isActive: Boolean(hz.isActive) });

        const sb = json.ads.find((a: any) => a.type === 'sidebar');
        if (sb) setSidebar({ code: sb.code, isActive: Boolean(sb.isActive) });
      }
    } catch (e) {
      console.error('Erro ao buscar ads:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (type: string, data: { code: string; isActive: boolean }) => {
    setSaving(true);
    try {
      await fetch('/api/admin/ads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          blogId,
          type,
          code: data.code,
          isActive: data.isActive
        })
      });
      alert(`Bloco ${type} salvo com sucesso!`);
    } catch (e) {
      alert('Erro ao salvar anúncio.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium text-sm">Carregando inventário de anúncios...</p>
      </div>
    );
  }

  return (
    <div className="max-w-[1200px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* HEADER */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            INVENTORY MANAGER • ADSENSE & NATIVE
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Gerenciador de Espaços Publicitários
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl">
            Cole os códigos HTML ou JavaScript fornecidos pelo Google AdSense, Taboola ou Outbrain nos espaços abaixo. A injeção no front-end será feita automaticamente.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* IN-ARTICLE (Agressivo) */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-emerald-900/50 p-6 shadow-xl flex flex-col relative overflow-hidden">
           <div className="absolute top-0 right-0 px-3 py-1 bg-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase rounded-bl-xl border-b border-l border-emerald-500/30">
             🔥 Maior Lucro
           </div>
           <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">📝 In-Article (Meio do Texto)</h2>
           <p className="text-xs text-slate-400 mb-4">Este bloco será injetado automaticamente a cada 3 parágrafos dentro de todos os artigos.</p>
           
           <textarea 
             className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-3 text-emerald-400 font-mono text-[10px] outline-none focus:border-emerald-500 transition-colors resize-none mb-4"
             placeholder="<!-- Cole o código do bloco de anúncios In-Article do AdSense aqui... -->"
             value={inArticle.code}
             onChange={(e) => setInArticle({...inArticle, code: e.target.value})}
           ></textarea>

           <div className="flex justify-between items-center mt-auto">
             <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
               <input type="checkbox" checked={inArticle.isActive} onChange={(e) => setInArticle({...inArticle, isActive: e.target.checked})} className="rounded bg-slate-800 border-slate-700 text-emerald-500 focus:ring-emerald-500" />
               Ativar Injeção
             </label>
             <button disabled={saving} onClick={() => handleSave('in_article', inArticle)} className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg">Salvar Bloco</button>
           </div>
        </div>

        {/* STICKY MOBILE */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-blue-900/50 p-6 shadow-xl flex flex-col relative overflow-hidden">
           <div className="absolute top-0 right-0 px-3 py-1 bg-blue-500/20 text-blue-400 text-[10px] font-black uppercase rounded-bl-xl border-b border-l border-blue-500/30">
             📱 Mobile 100% Viewability
           </div>
           <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">📱 Sticky Mobile (Rodapé)</h2>
           <p className="text-xs text-slate-400 mb-4">Banner flutuante que fica preso no rodapé (bottom-0) na visão de celulares.</p>
           
           <textarea 
             className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-3 text-blue-400 font-mono text-[10px] outline-none focus:border-blue-500 transition-colors resize-none mb-4"
             placeholder="<!-- Cole o código do banner 320x50 ou 320x100 do AdSense aqui... -->"
             value={stickyMobile.code}
             onChange={(e) => setStickyMobile({...stickyMobile, code: e.target.value})}
           ></textarea>

           <div className="flex justify-between items-center mt-auto">
             <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
               <input type="checkbox" checked={stickyMobile.isActive} onChange={(e) => setStickyMobile({...stickyMobile, isActive: e.target.checked})} className="rounded bg-slate-800 border-slate-700 text-blue-500 focus:ring-blue-500" />
               Ativar Sticky
             </label>
             <button disabled={saving} onClick={() => handleSave('sticky_mobile', stickyMobile)} className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg">Salvar Bloco</button>
           </div>
        </div>

        {/* HORIZONTAL BANNER */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl flex flex-col">
           <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">🖥️ Banner Horizontal (Middle)</h2>
           <p className="text-xs text-slate-400 mb-4">Aparece dividindo o feed de notícias na Home e no meio do Layout principal.</p>
           
           <textarea 
             className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-400 font-mono text-[10px] outline-none focus:border-slate-500 transition-colors resize-none mb-4"
             placeholder="<!-- Banner 728x90 HTML -->"
             value={horizontal.code}
             onChange={(e) => setHorizontal({...horizontal, code: e.target.value})}
           ></textarea>

           <div className="flex justify-between items-center mt-auto">
             <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
               <input type="checkbox" checked={horizontal.isActive} onChange={(e) => setHorizontal({...horizontal, isActive: e.target.checked})} className="rounded bg-slate-800 border-slate-700" />
               Ativar Banner
             </label>
             <button disabled={saving} onClick={() => handleSave('horizontal', horizontal)} className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg">Salvar Bloco</button>
           </div>
        </div>

        {/* SIDEBAR BANNER */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800 p-6 shadow-xl flex flex-col">
           <h2 className="text-lg font-bold text-white mb-2 flex items-center gap-2">📑 Banner Sidebar (Lateral)</h2>
           <p className="text-xs text-slate-400 mb-4">Aparece fixado na coluna direita no Desktop (Ideal para Native Ads ou 300x250).</p>
           
           <textarea 
             className="w-full h-32 bg-slate-950 border border-slate-800 rounded-xl p-3 text-slate-400 font-mono text-[10px] outline-none focus:border-slate-500 transition-colors resize-none mb-4"
             placeholder="<!-- Banner 300x250 HTML -->"
             value={sidebar.code}
             onChange={(e) => setSidebar({...sidebar, code: e.target.value})}
           ></textarea>

           <div className="flex justify-between items-center mt-auto">
             <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
               <input type="checkbox" checked={sidebar.isActive} onChange={(e) => setSidebar({...sidebar, isActive: e.target.checked})} className="rounded bg-slate-800 border-slate-700" />
               Ativar Sidebar
             </label>
             <button disabled={saving} onClick={() => handleSave('sidebar', sidebar)} className="bg-slate-700 hover:bg-slate-600 text-white px-5 py-2 rounded-xl text-xs font-bold transition-all shadow-lg">Salvar Bloco</button>
           </div>
        </div>

      </div>
    </div>
  );
}
