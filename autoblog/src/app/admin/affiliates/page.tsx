'use client';
import React, { useState, useEffect } from 'react';

export default function AffiliatesPanel() {
  const [links, setLinks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [newLink, setNewLink] = useState({ keyword: '', url: '', isActive: true });

  useEffect(() => {
    fetch('/api/admin/affiliates')
      .then(res => res.json())
      .then(data => {
        setLinks(data.links || []);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    try {
      const res = await fetch('/api/admin/affiliates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLink)
      });
      if (res.ok) {
        const data = await res.json();
        setLinks([data.link, ...links]);
        setNewLink({ keyword: '', url: '', isActive: true });
      }
    } catch (e) {
      console.error(e);
    }
  };

  const toggleLink = async (id: string, currentStatus: boolean) => {
    try {
      await fetch(`/api/admin/affiliates`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, isActive: !currentStatus })
      });
      setLinks(links.map(l => l.id === id ? { ...l, isActive: !currentStatus } : l));
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <div className="bg-gradient-to-r from-purple-900/40 to-slate-900/80 backdrop-blur-2xl p-8 rounded-3xl border border-purple-900/50 shadow-2xl relative overflow-hidden">
         <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-500/10 rounded-full blur-3xl pointer-events-none -mr-48 -mt-48" />
         <div className="relative z-10">
           <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold tracking-wide mb-3">
             <span className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" />
             SEO PROGRAMÁTICO & CPA
           </div>
           <h1 className="text-3xl font-extrabold text-white">Central de Afiliados</h1>
           <p className="text-slate-400 mt-2">Cadastre palavras-chave estratégicas. A Inteligência Artificial irá injetar seus links de afiliado automaticamente sempre que essa palavra for gerada nos artigos.</p>
         </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 bg-slate-900/80 p-6 rounded-3xl border border-slate-800 shadow-xl space-y-5 h-fit">
          <h3 className="text-lg font-bold text-white mb-4">Nova Armadilha de Link</h3>
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Palavra-Chave (Gatilho)</label>
            <input type="text" value={newLink.keyword} onChange={e => setNewLink({...newLink, keyword: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:border-purple-500 outline-none" placeholder="Ex: comprar bitcoin" />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-400 mb-1">Link de Afiliado (URL)</label>
            <input type="url" value={newLink.url} onChange={e => setNewLink({...newLink, url: e.target.value})} className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-purple-400 font-mono focus:border-purple-500 outline-none" placeholder="https://..." />
          </div>
          <button onClick={handleSave} className="w-full bg-purple-600 hover:bg-purple-500 text-white font-bold py-3 rounded-xl transition-all shadow-[0_0_15px_rgba(147,51,234,0.4)] mt-2">
            Salvar Regra
          </button>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-bold text-white mb-4">Gatilhos Ativos na Rede</h3>
          {loading ? (
             <div className="animate-pulse bg-slate-800/50 h-32 rounded-2xl w-full"></div>
          ) : links.length === 0 ? (
             <div className="bg-slate-900/50 p-10 rounded-2xl border border-slate-800 text-center text-slate-500">Nenhum gatilho de link de afiliado cadastrado.</div>
          ) : (
            links.map(link => (
              <div key={link.id} className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 flex justify-between items-center group hover:border-purple-500/50 transition-all">
                <div className="flex-1 overflow-hidden">
                  <div className="flex items-center gap-2">
                    <span className={`w-2 h-2 rounded-full min-w-[8px] ${link.isActive ? 'bg-purple-500 animate-pulse' : 'bg-red-500'}`}></span>
                    <h4 className="font-bold text-white text-md truncate">"{link.keyword}"</h4>
                  </div>
                  <a href={link.url} target="_blank" rel="noreferrer" className="text-xs text-slate-500 mt-1 font-mono truncate block hover:text-purple-400">
                    {link.url}
                  </a>
                </div>
                <div className="ml-4 flex-shrink-0">
                  <button 
                    onClick={() => toggleLink(link.id, link.isActive)}
                    className={`px-4 py-2 rounded-lg text-xs font-bold border transition-all ${link.isActive ? 'border-red-900/50 text-red-400 hover:bg-red-950' : 'border-purple-900/50 text-purple-400 hover:bg-purple-950'}`}
                  >
                    {link.isActive ? 'Pausar' : 'Ativar'}
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
