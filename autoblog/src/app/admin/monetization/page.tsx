'use client';
import React, { useState, useEffect } from 'react';

export default function MonetizationPanel() {
  const [ads, setAds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newAd, setNewAd] = useState({ name: '', position: 'article_top', scriptCode: '', isActive: true });

  useEffect(() => {
    fetch('/api/admin/ads')
      .then(res => res.json())
      .then(data => {
        setAds(data.ads || []);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    try {
      const res = await fetch('/api/admin/ads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAd)
      });
      if (res.ok) {
        const data = await res.json();
        setAds([data.ad, ...ads]);
        setNewAd({ name: '', position: 'article_top', scriptCode: '', isActive: true });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const toggleAd = async (id: string, currentStatus: boolean) => {
    try {
      await fetch(`/api/admin/ads`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, isActive: !currentStatus })
      });
      setAds(ads.map(ad => ad.id === id ? { ...ad, isActive: !currentStatus } : ad));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <div className="bg-gradient-to-r from-emerald-900/40 to-slate-900/80 backdrop-blur-2xl p-8 rounded-3xl border border-emerald-900/50 shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-3xl pointer-events-none -mr-48 -mt-48" />
         <div className="relative z-10">
           <h1 className="text-3xl font-extrabold text-white">Centro de Monetização</h1>
           <p className="text-slate-400 mt-2">Gerencie AdSense, VSLs e Iframes customizados para maximizar o RPM da Máfia de Blogs.</p>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 bg-slate-900/80 p-6 rounded-3xl border border-slate-800 shadow-xl space-y-5 h-fit">
          <h3 className="text-lg font-bold text-white mb-4">Novo Bloco (Ad/Iframe)</h3>
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Nome do Bloco</label>
            <input type="text" value={newAd.name} onChange={e => setNewAd({...newAd, name: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 outline-none" placeholder="Ex: Banner Topo AdSense" />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Posição</label>
            <select value={newAd.position} onChange={e => setNewAd({...newAd, position: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-emerald-500 outline-none">
              <option value="article_top">Topo do Artigo</option>
              <option value="article_middle">Meio do Artigo (In-text)</option>
              <option value="article_bottom">Fim do Artigo</option>
              <option value="sidebar">Sidebar (Desktop)</option>
              <option value="popup">Modal/Pop-up VSL</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Código HTML/JS/Iframe</label>
            <textarea value={newAd.scriptCode} onChange={e => setNewAd({...newAd, scriptCode: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-emerald-400 font-mono h-32 focus:border-emerald-500 outline-none" placeholder="<script async src='...'></script>" />
          </div>
          <button onClick={handleSave} className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(5,150,105,0.4)]">
            Injetar na Rede
          </button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-bold text-white mb-4">Blocos Ativos na Rede</h3>
          {loading ? (
             <div className="animate-pulse bg-slate-800/50 h-32 rounded-2xl w-full"></div>
          ) : ads.length === 0 ? (
             <div className="bg-slate-900/50 p-10 rounded-2xl border border-slate-800 text-center text-slate-500">Nenhum bloco de monetização criado. O servidor não vai se pagar sozinho!</div>
          ) : (
            ads.map(ad => (
              <div key={ad.id} className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 flex justify-between items-center group hover:border-emerald-500/50 transition-all">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full ${ad.isActive ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></span>
                    <h4 className="font-bold text-white text-md">{ad.name}</h4>
                  </div>
                  <p className="text-xs text-slate-500 mt-1 font-mono uppercase bg-slate-950 inline-block px-2 py-0.5 rounded border border-slate-800">
                    Posição: {ad.position}
                  </p>
                </div>
                <button 
                  onClick={() => toggleAd(ad.id, ad.isActive)}
                  className={`px-4 py-2 rounded-lg text-xs font-bold border transition-all ${ad.isActive ? 'border-red-900/50 text-red-400 hover:bg-red-950' : 'border-emerald-900/50 text-emerald-400 hover:bg-emerald-950'}`}
                >
                  {ad.isActive ? 'Pausar' : 'Ativar'}
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
