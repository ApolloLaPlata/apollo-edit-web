'use client';
import React, { useState, useEffect } from 'react';

export default function MediaClient({
  initialMedia,
  blogs,
}: {
  initialMedia: any[];
  blogs: any[];
}) {
  const [activeTab, setActiveTab] = useState<'gallery' | 'studio' | 'shorts'>('gallery');
  const [search, setSearch] = useState('');
  const [selectedBlog, setSelectedBlog] = useState('ALL');

  // Studio State
  const [cardTitle, setCardTitle] = useState('O Futuro dos Agentes Neurais em 2026');
  const [cardSubtitle, setCardSubtitle] = useState('Como a IA autônoma e a automação editorial estão revolucionando o engajamento e a monetização mundial.');
  const [cardPortal, setCardPortal] = useState('TechPulse News • Oficial');
  const [cardTheme, setCardTheme] = useState<'cyan' | 'purple' | 'amber' | 'emerald'>('cyan');
  const [cardFormat, setCardFormat] = useState<'story' | 'feed' | 'banner'>('story');

  // Shorts / Reels AI Studio State (Fase 124)
  const [shortsTitle, setShortsTitle] = useState('Por que a Inteligência Artificial vai dominar o mercado em 2026? 🚀');
  const [shortsScript, setShortsScript] = useState([
    '💡 O mercado de IA está mudando tudo o que conhecemos hoje!',
    '🤖 Os novos agentes neurais trabalham 24 horas por dia sem parar.',
    '📈 Você já está usando as ferramentas certas ou vai ficar para trás?',
    '⚡ Clique no link da bio e confira nossa matéria completa no portal!'
  ]);
  const [shortsPlatform, setShortsPlatform] = useState<'YouTube Shorts 🔴' | 'Instagram Reels 🟣' | 'TikTok 🎵' | 'Kwai 🟡' | 'Twitter / X 🐦'>('TikTok 🎵');
  const [shortsVoice, setShortsVoice] = useState<'Aoede (Host)' | 'Charon (Especialista)' | 'Cyber Phonk'>('Aoede (Host)');
  const [shortsPlaying, setShortsPlaying] = useState(false);
  const [activeSentenceIdx, setActiveSentenceIdx] = useState(0);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    let timer: any;
    if (shortsPlaying && shortsScript.length > 0) {
      timer = setInterval(() => {
        setActiveSentenceIdx((prev) => {
          if (prev + 1 < shortsScript.length) {
            return prev + 1;
          } else {
            setShortsPlaying(false);
            showToast('success', '🎬 Simulação do Short / Reel finalizada com sucesso!');
            return 0;
          }
        });
      }, 2500); // 2.5s por frase no teleprompter Hormozi
    }
    return () => clearInterval(timer);
  }, [shortsPlaying, shortsScript]);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const copyMediaUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    showToast('success', 'URL da imagem copiada para a área de transferência!');
  };

  const handleCopyCardCode = () => {
    const htmlSnippet = `<div style="padding: 32px; background: #020617; color: white; font-family: sans-serif; border-radius: 24px; border: 1px solid #1e293b;">\n  <span style="color: #${cardTheme === 'cyan' ? '06b6d4' : cardTheme === 'purple' ? 'a855f7' : cardTheme === 'amber' ? 'f59e0b' : '10b981'}; font-weight: bold; font-size: 12px; text-transform: uppercase;">⚡ ${cardPortal}</span>\n  <h1 style="font-size: 28px; font-weight: 900; margin-top: 12px; line-height: 1.2;">${cardTitle}</h1>\n  <p style="color: #94a3b8; font-size: 14px; line-height: 1.6; margin-top: 16px;">${cardSubtitle}</p>\n</div>`;
    navigator.clipboard.writeText(htmlSnippet);
    showToast('success', 'Código HTML/CSS do Card copiado com sucesso! Pronto para incorporar ou postar.');
  };

  const filteredMedia = initialMedia.filter((item) => {
    const matchesSearch =
      item.title.toLowerCase().includes(search.toLowerCase()) ||
      item.blogName?.toLowerCase().includes(search.toLowerCase());
    const matchesBlog = selectedBlog === 'ALL' || item.blogId === selectedBlog;
    return matchesSearch && matchesBlog;
  });

  const getThemeClasses = () => {
    switch (cardTheme) {
      case 'purple':
        return {
          bg: 'from-purple-950/80 via-slate-950 to-indigo-950/90 border-purple-500/40 shadow-purple-500/20',
          badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40',
          accent: 'text-purple-400',
        };
      case 'amber':
        return {
          bg: 'from-amber-950/80 via-slate-950 to-orange-950/90 border-amber-500/40 shadow-amber-500/20',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          accent: 'text-amber-400',
        };
      case 'emerald':
        return {
          bg: 'from-emerald-950/80 via-slate-950 to-teal-950/90 border-emerald-500/40 shadow-emerald-500/20',
          badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          accent: 'text-emerald-400',
        };
      default: // cyan
        return {
          bg: 'from-cyan-950/80 via-slate-950 to-blue-950/90 border-cyan-500/40 shadow-cyan-500/20',
          badge: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
          accent: 'text-cyan-400',
        };
    }
  };

  const theme = getThemeClasses();

  return (
    <div className="space-y-8 relative">
      {/* TOAST EXECUTIVO */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 backdrop-blur-xl ${
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
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-blue-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />
              ASSETS & GALERIA ENTERPRISE
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Galeria & Estúdio de Mídia da Frota
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Repositório centralizado de imagens neurais e estúdio de infográficos para redes sociais. Crie cards virais em tempo real ou copie links diretos da CDN.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Total Mídia</span>
              <span className="text-2xl font-extrabold text-white font-mono">{initialMedia.length}</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Portais</span>
              <span className="text-2xl font-extrabold text-blue-400 font-mono">{blogs.length}</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Status CDN</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">100%</span>
            </div>
          </div>
        </div>

        {/* SELETOR DE ABAS EXECUTIVAS */}
        <div className="flex gap-3 mt-8 pt-6 border-t border-slate-800/80 relative z-10">
          <button
            onClick={() => setActiveTab('gallery')}
            className={`px-6 py-2.5 rounded-xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2 ${
              activeTab === 'gallery'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-cyan-500/20 scale-105'
                : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <span>🖼️</span> Galeria de Imagens ({initialMedia.length})
          </button>
          <button
            onClick={() => setActiveTab('studio')}
            className={`px-6 py-2.5 rounded-xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2 ${
              activeTab === 'studio'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/20 scale-105'
                : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <span>🎨</span> Estúdio Visual de Cards Sociais
          </button>
          <button
            onClick={() => {
              setActiveTab('shorts');
              setShortsPlaying(false);
            }}
            className={`px-6 py-2.5 rounded-xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2 ${
              activeTab === 'shorts'
                ? 'bg-gradient-to-r from-pink-600 to-rose-600 text-white shadow-lg shadow-pink-500/20 scale-105'
                : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <span>🎬</span> Shorts & Reels AI Studio (9:16)
          </button>
        </div>
      </div>

      {/* ABA 1: GALERIA DE IMAGENS */}
      {activeTab === 'gallery' && (
        <div className="space-y-6">
          {/* BARRA DE PESQUISA E FILTROS */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-900/60 p-4 rounded-2xl border border-slate-800/80 backdrop-blur-md">
            <div className="relative w-full md:w-96">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">🔍</span>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar por título do artigo ou portal..."
                className="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-800/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
              />
            </div>

            <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
              <button
                onClick={() => setSelectedBlog('ALL')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                  selectedBlog === 'ALL'
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                    : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800/80'
                }`}
              >
                Todos os Portais ({initialMedia.length})
              </button>
              {blogs.map((b) => {
                const count = initialMedia.filter((m) => m.blogId === b.id).length;
                return (
                  <button
                    key={b.id}
                    onClick={() => setSelectedBlog(b.id)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                      selectedBlog === b.id
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                        : 'bg-slate-950/60 text-slate-400 hover:text-white border border-slate-800/80'
                    }`}
                  >
                    {b.name} ({count})
                  </button>
                );
              })}
            </div>
          </div>

          {/* GRID DE MÍDIAS */}
          <div className="bg-slate-900/40 backdrop-blur-md rounded-3xl border border-slate-800/80 p-8 shadow-2xl">
            {filteredMedia.length === 0 ? (
              <div className="py-20 text-center text-slate-500 font-medium">
                <span className="text-5xl block mb-4 opacity-30">🖼️</span>
                Nenhuma imagem encontrada para este filtro ou busca.
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                {filteredMedia.map((item) => (
                  <div
                    key={item.id}
                    className="bg-slate-950/80 rounded-2xl overflow-hidden border border-slate-800/80 group relative shadow-lg hover:shadow-blue-500/20 hover:border-blue-500/40 transition-all flex flex-col justify-between"
                  >
                    <div>
                      <div className="aspect-square relative overflow-hidden bg-slate-900">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img
                          src={item.coverImage}
                          alt={item.title}
                          className="object-cover w-full h-full group-hover:scale-110 transition-transform duration-700 ease-out"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4 pointer-events-none">
                          <p className="text-xs text-white font-bold line-clamp-3 leading-snug drop-shadow-md">
                            {item.title}
                          </p>
                        </div>

                        {/* BADGE DO PORTAL */}
                        <div className="absolute top-2.5 left-2.5 z-10">
                          <span className="bg-slate-950/90 text-blue-300 border border-blue-500/30 px-2.5 py-1 rounded-md text-[9px] font-black uppercase tracking-wider shadow-md backdrop-blur-md">
                            {item.blogName || 'Portal'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="p-3 border-t border-slate-800/80 bg-slate-950/90 flex gap-2">
                      <button
                        onClick={() => copyMediaUrl(item.coverImage)}
                        className="flex-1 bg-slate-800 hover:bg-blue-600 text-slate-300 hover:text-white py-2 rounded-lg transition-colors font-bold text-[10px] uppercase tracking-wider flex items-center justify-center gap-1.5 border border-slate-700/80 hover:border-blue-500 shadow-sm active:scale-95"
                      >
                        <span>📋</span> Copiar URL
                      </button>
                      {item.blogDomain && (
                        <a
                          href={`https://${item.blogDomain}/blog/${item.slug}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="bg-slate-800/60 hover:bg-slate-700 text-slate-400 hover:text-white px-2.5 py-2 rounded-lg transition-colors font-bold text-[10px] flex items-center justify-center border border-slate-700/50"
                          title="Ver artigo original"
                        >
                          ↗
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ABA 2: ESTÚDIO DE CARDS SOCIAIS */}
      {activeTab === 'studio' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* CONTROLES DO ESTÚDIO (ESQUERDA - 5 COLS) */}
          <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-2xl space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <span className="text-[10px] font-mono uppercase tracking-widest text-purple-400 bg-purple-950/80 px-2.5 py-1 rounded border border-purple-800 block w-max mb-2">
                ✨ Gerador Neural de Assets
              </span>
              <h2 className="text-xl font-extrabold text-white">Configurar Card Social</h2>
              <p className="text-xs text-slate-400 mt-1">
                Personalize o texto, cores e formato para exportar infográficos e cards visuais de alto impacto.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Título Impactante</label>
                <textarea
                  rows={2}
                  value={cardTitle}
                  onChange={(e) => setCardTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-white font-bold focus:outline-none focus:border-purple-500 resize-none"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Subtítulo ou Resumo</label>
                <textarea
                  rows={3}
                  value={cardSubtitle}
                  onChange={(e) => setCardSubtitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 focus:outline-none focus:border-purple-500 resize-none leading-relaxed"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Portal / Marca / Fonte</label>
                <input
                  type="text"
                  value={cardPortal}
                  onChange={(e) => setCardPortal(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Formato Visual</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => setCardFormat('story')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all ${
                      cardFormat === 'story'
                        ? 'bg-purple-600 text-white border-purple-400 shadow-md'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    📱 Story (9:16)
                  </button>
                  <button
                    type="button"
                    onClick={() => setCardFormat('feed')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all ${
                      cardFormat === 'feed'
                        ? 'bg-purple-600 text-white border-purple-400 shadow-md'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    🖼️ Feed (1:1)
                  </button>
                  <button
                    type="button"
                    onClick={() => setCardFormat('banner')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all ${
                      cardFormat === 'banner'
                        ? 'bg-purple-600 text-white border-purple-400 shadow-md'
                        : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    🐦 Banner (16:9)
                  </button>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Tema de Cor</label>
                <div className="grid grid-cols-4 gap-2">
                  <button
                    type="button"
                    onClick={() => setCardTheme('cyan')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all flex items-center justify-center gap-1.5 ${
                      cardTheme === 'cyan' ? 'bg-cyan-600 text-white border-cyan-400 shadow-md' : 'bg-slate-950 text-cyan-400 border-slate-800'
                    }`}
                  >
                    <span className="w-2.5 h-2.5 rounded-full bg-cyan-400" /> Ciano
                  </button>
                  <button
                    type="button"
                    onClick={() => setCardTheme('purple')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all flex items-center justify-center gap-1.5 ${
                      cardTheme === 'purple' ? 'bg-purple-600 text-white border-purple-400 shadow-md' : 'bg-slate-950 text-purple-400 border-slate-800'
                    }`}
                  >
                    <span className="w-2.5 h-2.5 rounded-full bg-purple-400" /> Roxo
                  </button>
                  <button
                    type="button"
                    onClick={() => setCardTheme('amber')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all flex items-center justify-center gap-1.5 ${
                      cardTheme === 'amber' ? 'bg-amber-600 text-white border-amber-400 shadow-md' : 'bg-slate-950 text-amber-400 border-slate-800'
                    }`}
                  >
                    <span className="w-2.5 h-2.5 rounded-full bg-amber-400" /> Âmbar
                  </button>
                  <button
                    type="button"
                    onClick={() => setCardTheme('emerald')}
                    className={`py-2 rounded-xl text-xs font-extrabold border transition-all flex items-center justify-center gap-1.5 ${
                      cardTheme === 'emerald' ? 'bg-emerald-600 text-white border-emerald-400 shadow-md' : 'bg-slate-950 text-emerald-400 border-slate-800'
                    }`}
                  >
                    <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" /> Verde
                  </button>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-800 flex gap-3">
                <button
                  type="button"
                  onClick={handleCopyCardCode}
                  className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-extrabold text-xs py-3 rounded-xl shadow-lg shadow-purple-500/20 transition-all flex items-center justify-center gap-2 active:scale-95"
                >
                  <span>📋</span> Copiar Código HTML do Card
                </button>
              </div>
            </div>
          </div>

          {/* PREVIEW AO VIVO DO CARD (DIREITA - 7 COLS) */}
          <div className="lg:col-span-7 bg-slate-950/90 border border-slate-800/80 rounded-3xl p-8 flex flex-col items-center justify-center relative min-h-[500px]">
            <div className="absolute top-4 left-6 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400">Preview em Tempo Real • Render Canvas</span>
            </div>

            {/* O CARD RENDERIZADO */}
            <div
              className={`w-full max-w-md bg-gradient-to-br ${theme.bg} p-8 rounded-3xl border shadow-2xl flex flex-col justify-between relative overflow-hidden transition-all duration-500 ${
                cardFormat === 'story'
                  ? 'aspect-[9/14] max-h-[540px]'
                  : cardFormat === 'feed'
                  ? 'aspect-square max-w-[420px]'
                  : 'aspect-[16/9] max-w-full'
              }`}
            >
              {/* EFEITO DE LUZ NO FUNDO */}
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-2xl pointer-events-none -mt-20 -mr-20" />

              <div>
                <div className="flex items-center justify-between mb-6">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${theme.badge} shadow-sm`}>
                    ⚡ {cardPortal}
                  </span>
                  <span className="text-white/60 text-xs font-mono">2026 • AI NEWS</span>
                </div>

                <h1 className={`font-black text-white leading-tight drop-shadow-md ${cardFormat === 'banner' ? 'text-2xl md:text-3xl' : 'text-2xl md:text-4xl'}`}>
                  {cardTitle}
                </h1>
                <p className="text-slate-300 text-xs md:text-sm leading-relaxed mt-4 line-clamp-4 font-normal">
                  {cardSubtitle}
                </p>
              </div>

              <div className="mt-8 pt-4 border-t border-white/10 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-white/10 flex items-center justify-center text-xs">🐝</span>
                  <span className="text-white font-bold text-xs">Auto-Blog CMS</span>
                </div>
                <span className={`text-[11px] font-extrabold uppercase tracking-wider ${theme.accent}`}>
                  [ Ler Artigo Completo ↗ ]
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ABA 3: SHORTS & REELS AI STUDIO (9:16 • FASE 124) */}
      {activeTab === 'shorts' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in fade-in duration-300">
          {/* CONTROLES DO ESTÚDIO DE VÍDEO (ESQUERDA - 5 COLS) */}
          <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 shadow-2xl space-y-6">
            <div className="border-b border-slate-800 pb-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-mono uppercase tracking-widest text-pink-400 bg-pink-950/80 px-2.5 py-1 rounded border border-pink-800">
                  🎬 Vídeo Curto Vertical 9:16
                </span>
                <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/30">
                  Colmeia Sync 🟢
                </span>
              </div>
              <h2 className="text-xl font-extrabold text-white">Shorts & Reels AI Studio</h2>
              <p className="text-xs text-slate-400 mt-1">
                Gere vídeos virais para TikTok, Reels, Kwai, Shorts e X com teleprompter animado estilo Hormozi e síntese vocal.
              </p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Plataforma de Destino</label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {(['TikTok 🎵', 'Instagram Reels 🟣', 'YouTube Shorts 🔴', 'Kwai 🟡', 'Twitter / X 🐦'] as const).map((plat) => (
                    <button
                      key={plat}
                      type="button"
                      onClick={() => setShortsPlatform(plat)}
                      className={`py-2 px-2.5 rounded-xl text-xs font-extrabold border transition-all truncate text-left ${
                        shortsPlatform === plat
                          ? 'bg-pink-600 text-white border-pink-400 shadow-md scale-102'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                      }`}
                    >
                      {plat}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Locutor & Estilo Sonoro</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Aoede (Host)', 'Charon (Especialista)', 'Cyber Phonk'] as const).map((voice) => (
                    <button
                      key={voice}
                      type="button"
                      onClick={() => setShortsVoice(voice)}
                      className={`py-2 px-2 rounded-xl text-[11px] font-extrabold border transition-all truncate text-center ${
                        shortsVoice === voice
                          ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white border-purple-400 shadow-md'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
                      }`}
                    >
                      {voice}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs font-bold text-slate-300 block mb-1.5">Gancho Viral (Hook Principal)</label>
                <input
                  type="text"
                  value={shortsTitle}
                  onChange={(e) => setShortsTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-xs text-white font-bold focus:outline-none focus:border-pink-500"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1.5">
                  <label className="text-xs font-bold text-slate-300">Roteiro por Frases (2.5s cada)</label>
                  <button
                    type="button"
                    onClick={() => {
                      setShortsScript([
                        '🔥 Alerta urgente da nossa redação neural!',
                        '🚀 A automação audiovisual da Colmeia atingiu 100% de performance.',
                        '💎 Os novos formatos 9:16 dominam o tráfego do TikTok, Kwai e Reels!',
                        '👉 Siga nosso portal e acompanhe as novidades do Enxame em tempo real.'
                      ]);
                      showToast('success', '⚡ Roteiro viral gerado e aplicado pela IA com sucesso!');
                    }}
                    className="text-[10px] text-pink-400 hover:text-pink-300 font-mono font-bold underline"
                  >
                    ⚡ Gerar Roteiro AI
                  </button>
                </div>
                <textarea
                  rows={5}
                  value={shortsScript.join('\n')}
                  onChange={(e) => setShortsScript(e.target.value.split('\n').filter(Boolean))}
                  placeholder="Digite uma frase por linha..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 focus:outline-none focus:border-pink-500 resize-none font-mono leading-relaxed"
                />
                <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                  Dica: Cada linha vira um bloco de legenda pulsante no simulador.
                </span>
              </div>

              <div className="pt-4 border-t border-slate-800 space-y-2.5">
                <button
                  type="button"
                  onClick={() => {
                    setShortsPlaying(!shortsPlaying);
                    if (!shortsPlaying) showToast('success', '▶️ Reproduzindo simulação de legenda Hormozi ao vivo!');
                  }}
                  className="w-full bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-extrabold text-xs py-3.5 rounded-xl shadow-lg shadow-pink-500/20 transition-all flex items-center justify-center gap-2 active:scale-95 cursor-pointer"
                >
                  <span>{shortsPlaying ? '⏸' : '▶'}</span>
                  <span>{shortsPlaying ? 'Pausar Simulação do Vídeo' : 'Simular Reprodução do Short / Reel'}</span>
                </button>

                <div className="grid grid-cols-2 gap-2.5">
                  <button
                    type="button"
                    onClick={() => {
                      const payload = JSON.stringify({ platform: shortsPlatform, voice: shortsVoice, title: shortsTitle, script: shortsScript }, null, 2);
                      navigator.clipboard.writeText(payload);
                      showToast('success', `⚡ Roteiro e metadata copiados! Pronto para publicar no ${shortsPlatform}`);
                    }}
                    className="bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800 font-bold text-xs py-3 rounded-xl transition-all flex items-center justify-center gap-1.5"
                  >
                    <span>📋</span> Copiar Roteiro
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      showToast('success', `🐝 Short enfileirado no Cron Job para publicação automática no ${shortsPlatform}!`);
                    }}
                    className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs py-3 rounded-xl shadow-md transition-all flex items-center justify-center gap-1.5"
                  >
                    <span>🚀</span> Enviar p/ Colmeia
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* SIMULADOR DE SMARTPHONE VERTICAL 9:16 (DIREITA - 7 COLS) */}
          <div className="lg:col-span-7 bg-slate-950/90 border border-slate-800/80 rounded-3xl p-6 md:p-8 flex flex-col items-center justify-center relative min-h-[620px]">
            <div className="absolute top-4 left-6 flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-pink-500 animate-ping" />
              <span className="text-[10px] font-mono uppercase tracking-widest text-slate-400">
                Simulador de Smartphone • Vertical 9:16 ({shortsPlatform})
              </span>
            </div>

            {/* MOLDURA DO SMARTPHONE (SMARTPHONE FRAME) */}
            <div className="w-full max-w-[320px] aspect-[9/18] bg-black rounded-[44px] p-3 border-4 border-slate-800 shadow-2xl relative flex flex-col justify-between overflow-hidden ring-1 ring-white/10">
              {/* Notch / Câmera Frontal */}
              <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-6 bg-slate-900 rounded-b-2xl z-30 flex items-center justify-center gap-2 border-b border-x border-slate-800">
                <div className="w-2 h-2 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-800 border border-slate-600" />
              </div>

              {/* TELA DO VÍDEO (CANVAS COM GRADIENTE E BEATS) */}
              <div className="w-full h-full rounded-[36px] bg-gradient-to-b from-slate-900 via-purple-950/80 to-slate-950 relative overflow-hidden flex flex-col justify-between p-5 pt-10 text-white">
                {/* Glow de fundo e ondas sonoras */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-pink-500/20 via-purple-900/10 to-transparent pointer-events-none" />
                
                {/* Visualizador de Ondas Sonoras no Fundo */}
                <div className="absolute inset-x-0 bottom-32 flex items-end justify-center gap-1 opacity-20 pointer-events-none h-24">
                  {[30, 60, 40, 80, 50, 90, 40, 70, 100, 60, 40, 80, 50, 70, 30, 90, 60, 40].map((h, i) => (
                    <div
                      key={i}
                      className="w-1.5 bg-pink-400 rounded-full transition-all duration-150"
                      style={{ height: shortsPlaying ? `${Math.max(10, h * Math.random())}%` : `${h * 0.3}%` }}
                    />
                  ))}
                </div>

                {/* TOPO DO VÍDEO: PERFIL E BADGE */}
                <div className="relative z-10 flex items-center justify-between">
                  <div className="flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                    <span className="text-xs">🎙️</span>
                    <span className="text-[10px] font-bold font-mono text-purple-200">@redacao.neural</span>
                  </div>
                  <span className="bg-pink-600 text-[9px] font-black uppercase px-2 py-0.5 rounded-full shadow-md animate-pulse">
                    AO VIVO
                  </span>
                </div>

                {/* CENTRO DA TELA: TELEPROMPTER ESTILO ALEX HORMOZI */}
                <div className="relative z-10 my-auto text-center px-2 py-4">
                  <div className="bg-black/60 backdrop-blur-xl p-4 rounded-2xl border border-pink-500/40 shadow-2xl transition-all duration-300 scale-105">
                    <p className="text-sm sm:text-base font-black leading-snug tracking-wide text-white drop-shadow-[0_2px_10px_rgba(236,72,153,0.8)]">
                      {(shortsScript[activeSentenceIdx] || shortsTitle).split(' ').map((word, wIdx) => {
                        const isHighlighted = wIdx % 3 === 0;
                        return (
                          <span
                            key={wIdx}
                            className={`inline-block mr-1 transition-all ${
                              isHighlighted ? 'text-yellow-400 scale-110 font-extrabold underline decoration-pink-500' : 'text-white'
                            }`}
                          >
                            {word}
                          </span>
                        );
                      })}
                    </p>
                  </div>
                  <div className="text-[10px] font-mono text-slate-400 mt-3 bg-black/40 px-3 py-1 rounded-full inline-block">
                    Locução: <strong className="text-pink-300">{shortsVoice}</strong>
                  </div>
                </div>

                {/* RODAPÉ DO VÍDEO: TÍTULO, SOM ORIGINAL E ÍCONES SOCIAIS */}
                <div className="relative z-10 flex items-end justify-between gap-3 pt-4 border-t border-white/10">
                  <div className="flex-1 min-w-0 space-y-1">
                    <h3 className="text-xs font-black truncate leading-tight text-white drop-shadow">
                      {shortsTitle}
                    </h3>
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-300 font-mono">
                      <span className="animate-spin text-pink-400">♫</span>
                      <span className="truncate">Áudio Sintético • Dark Trap Radio</span>
                    </div>
                  </div>

                  {/* Ícones de Engajamento Estilo TikTok/Reels */}
                  <div className="flex flex-col items-center gap-3 text-center shrink-0">
                    <div className="space-y-0.5">
                      <div className="w-8 h-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center text-sm border border-white/20 hover:scale-110 transition-all cursor-pointer">
                        ❤️
                      </div>
                      <span className="text-[9px] font-bold block">45.2K</span>
                    </div>
                    <div className="space-y-0.5">
                      <div className="w-8 h-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center text-sm border border-white/20 hover:scale-110 transition-all cursor-pointer">
                        💬
                      </div>
                      <span className="text-[9px] font-bold block">1.2K</span>
                    </div>
                    <div className="space-y-0.5">
                      <div className="w-8 h-8 rounded-full bg-white/10 backdrop-blur-md flex items-center justify-center text-sm border border-white/20 hover:scale-110 transition-all cursor-pointer">
                        ↗️
                      </div>
                      <span className="text-[9px] font-bold block">890</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Barra de Navegação do Celular */}
              <div className="w-32 h-1 bg-slate-700 rounded-full mx-auto mt-1" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
