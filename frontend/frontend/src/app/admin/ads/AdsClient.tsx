'use client';
import React, { useState, useEffect } from 'react';
import { saveAdConfig } from './actions';

export default function AdsClient({
  blogs,
  initialAds,
}: {
  blogs: any[];
  initialAds: any[];
}) {
  const [selectedBlogId, setSelectedBlogId] = useState<string>(blogs[0]?.id || '');
  const [horizontal, setHorizontal] = useState('');
  const [square, setSquare] = useState('');
  const [vertical, setVertical] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  useEffect(() => {
    if (!selectedBlogId) return;
    const blogAds = initialAds.filter((a) => a.blogId === selectedBlogId);
    const hor = blogAds.find((a) => a.type === 'horizontal')?.code || '';
    const sq = blogAds.find((a) => a.type === 'square')?.code || '';
    const ver = blogAds.find((a) => a.type === 'vertical')?.code || '';

    setHorizontal(hor);
    setSquare(sq);
    setVertical(ver);
  }, [selectedBlogId, initialAds]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBlogId) return;

    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('blogId', selectedBlogId);
      formData.append('horizontalCode', horizontal);
      formData.append('squareCode', square);
      formData.append('verticalCode', vertical);

      await saveAdConfig(formData);
      showToast('success', 'Inventário de anúncios salvo e sincronizado em toda a CDN!');
    } catch (e: any) {
      showToast('error', 'Falha ao salvar scripts de publicidade.');
    } finally {
      setSubmitting(false);
    }
  };

  const countActiveScripts = () => {
    let count = 0;
    if (horizontal.trim()) count++;
    if (square.trim()) count++;
    if (vertical.trim()) count++;
    return count;
  };

  return (
    <div className="space-y-10 relative">
      {/* TOAST EXECUTIVO */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/90 border-red-500/50 text-red-300'
          }`}
        >
          <span className="text-lg">{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span className="text-xs font-semibold">{toast.message}</span>
          <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      {/* HEADER CORPORATIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-cyan-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              ADSENSE & TABOOLA ENTERPRISE
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Inventário de Publicidade (Ads)
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Gerencie os códigos publicitários do Google AdSense, Taboola, Outbrain e banners nativos para cada veículo da frota. Os scripts são injetados automaticamente sem quebrar a velocidade da página.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Veículos</span>
              <span className="text-2xl font-extrabold text-white font-mono">{blogs.length}</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Slots Ativos</span>
              <span className="text-2xl font-extrabold text-cyan-400 font-mono">{countActiveScripts()} / 3</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Injeção</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">Async</span>
            </div>
          </div>
        </div>
      </div>

      {/* SELETOR DE VEÍCULO */}
      <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-slate-800/80 p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🎯</span>
          <div>
            <h2 className="text-base font-bold text-white">Veículo Alvo de Monetização</h2>
            <p className="text-xs text-slate-400">Selecione para qual portal você deseja editar os scripts publicitários.</p>
          </div>
        </div>

        <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 w-full sm:w-auto">
          {blogs.map((blog) => (
            <button
              key={blog.id}
              onClick={() => setSelectedBlogId(blog.id)}
              className={`px-4 py-2.5 rounded-xl font-bold text-xs transition-all whitespace-nowrap border ${
                selectedBlogId === blog.id
                  ? 'bg-cyan-600 text-white border-cyan-500 shadow-lg shadow-cyan-500/20'
                  : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              }`}
            >
              {blog.name}
            </button>
          ))}
        </div>
      </div>

      {/* FORMULÁRIO DE SCRIPTS PUBLICITÁRIOS */}
      {selectedBlogId ? (
        <form onSubmit={handleSave} className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* BANNER HORIZONTAL */}
            <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col transition-all hover:border-cyan-500/40 group">
              <div className="flex items-center gap-4 mb-6 border-b border-slate-800/80 pb-4">
                <div className="w-12 h-8 bg-cyan-950/80 rounded-lg flex items-center justify-center border border-cyan-500/30">
                  <span className="block w-6 h-1.5 bg-cyan-400 rounded-full" />
                </div>
                <div>
                  <h3 className="font-extrabold text-white text-base">Banner Horizontal</h3>
                  <p className="text-[10px] text-cyan-400 uppercase tracking-widest font-bold">Topo e Meio de Artigos</p>
                </div>
              </div>
              <textarea
                value={horizontal}
                onChange={(e) => setHorizontal(e.target.value)}
                className="w-full bg-slate-950/80 text-slate-300 p-4 rounded-2xl font-mono text-xs h-56 border border-slate-800/80 focus:border-cyan-500 outline-none resize-none flex-grow shadow-inner"
                placeholder="<!-- Cole a tag <script> ou HTML do banner horizontal aqui -->"
              />
            </div>

            {/* BANNER QUADRADO */}
            <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col transition-all hover:border-purple-500/40 group">
              <div className="flex items-center gap-4 mb-6 border-b border-slate-800/80 pb-4">
                <div className="w-10 h-10 bg-purple-950/80 rounded-lg flex items-center justify-center border border-purple-500/30">
                  <span className="block w-4 h-4 bg-purple-400 rounded-sm" />
                </div>
                <div>
                  <h3 className="font-extrabold text-white text-base">Banner Quadrado (300x250)</h3>
                  <p className="text-[10px] text-purple-400 uppercase tracking-widest font-bold">Barra Lateral & Widgets</p>
                </div>
              </div>
              <textarea
                value={square}
                onChange={(e) => setSquare(e.target.value)}
                className="w-full bg-slate-950/80 text-slate-300 p-4 rounded-2xl font-mono text-xs h-56 border border-slate-800/80 focus:border-purple-500 outline-none resize-none flex-grow shadow-inner"
                placeholder="<!-- Cole a tag <script> ou HTML do banner quadrado aqui -->"
              />
            </div>

            {/* BANNER VERTICAL */}
            <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl p-8 border border-slate-800/80 shadow-2xl flex flex-col transition-all hover:border-emerald-500/40 group">
              <div className="flex items-center gap-4 mb-6 border-b border-slate-800/80 pb-4">
                <div className="w-8 h-12 bg-emerald-950/80 rounded-lg flex items-center justify-center border border-emerald-500/30">
                  <span className="block w-2 h-6 bg-emerald-400 rounded-sm" />
                </div>
                <div>
                  <h3 className="font-extrabold text-white text-base">Banner Vertical (Sticky)</h3>
                  <p className="text-[10px] text-emerald-400 uppercase tracking-widest font-bold">Anúncio Fixo no Rodapé</p>
                </div>
              </div>
              <textarea
                value={vertical}
                onChange={(e) => setVertical(e.target.value)}
                className="w-full bg-slate-950/80 text-slate-300 p-4 rounded-2xl font-mono text-xs h-56 border border-slate-800/80 focus:border-emerald-500 outline-none resize-none flex-grow shadow-inner"
                placeholder="<!-- Cole a tag <script> ou HTML do banner vertical aqui -->"
              />
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              disabled={submitting}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white px-8 py-4 rounded-2xl font-extrabold shadow-lg shadow-cyan-500/20 hover:scale-105 active:scale-95 transition-all text-sm uppercase tracking-wider flex items-center gap-2.5"
            >
              {submitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Sincronizando Anúncios...</span>
                </>
              ) : (
                <>
                  <span>🚀</span>
                  <span>Salvar Inventário Publicitário</span>
                </>
              )}
            </button>
          </div>
        </form>
      ) : (
        <div className="bg-slate-900/40 border-2 border-dashed border-slate-800 rounded-3xl h-64 flex flex-col items-center justify-center text-slate-500">
          <span className="text-4xl mb-3 opacity-30">🎯</span>
          <p className="font-bold text-sm">Selecione um veículo acima para configurar os espaços publicitários.</p>
        </div>
      )}
    </div>
  );
}
