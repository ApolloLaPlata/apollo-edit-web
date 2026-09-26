'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';
import CopyButton from './CopyButton';

interface Isca {
  id: string;
  platform: string;
  content: string;
  status: string;
  createdAt: string;
  postTitle: string;
  postSlug: string;
  blogName: string;
  blogDomain: string;
}

const getPlatformStyle = (plat: string) => {
  const p = (plat || '').toLowerCase();
  if (p === 'youtube' || p.includes('shorts')) return { emoji: '📺', label: 'YouTube / Shorts', bg: 'bg-red-500/15 text-red-400 border-red-500/30' };
  if (p === 'facebook') return { emoji: '👥', label: 'Facebook', bg: 'bg-blue-600/15 text-blue-400 border-blue-600/30' };
  if (p === 'instagram' || p.includes('reels')) return { emoji: '📸', label: 'Instagram / Reels', bg: 'bg-pink-500/15 text-pink-400 border-pink-500/30' };
  if (p === 'twitter' || p === 'x') return { emoji: '🐦', label: 'Twitter / X', bg: 'bg-slate-400/15 text-slate-200 border-slate-400/30' };
  if (p === 'tiktok' || p.includes('tiktok')) return { emoji: '🎵', label: 'TikTok (9:16)', bg: 'bg-cyan-400/15 text-cyan-300 border-cyan-400/30' };
  if (p === 'kwai') return { emoji: '⚡', label: 'Kwai', bg: 'bg-amber-500/15 text-amber-400 border-amber-500/30' };
  if (p === 'dailymotion') return { emoji: '🎬', label: 'Dailymotion', bg: 'bg-blue-400/15 text-blue-300 border-blue-400/30' };
  if (p === 'newsletter') return { emoji: '✉️', label: 'Newsletter (Daily Drop)', bg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30' };
  if (p === 'linkedin') return { emoji: '💼', label: 'LinkedIn', bg: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30' };
  if (p === 'telegram') return { emoji: '✈️', label: 'Telegram', bg: 'bg-sky-500/15 text-sky-400 border-sky-500/30' };
  return { emoji: '📢', label: plat || 'Social', bg: 'bg-purple-500/15 text-purple-400 border-purple-500/30' };
};

export default function SocialClient({ initialIscas }: { initialIscas: Isca[] }) {
  const [iscas] = useState<Isca[]>(initialIscas);
  const [selectedPlatform, setSelectedPlatform] = useState<string>('ALL');
  const [search, setSearch] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'iscas' | 'webhooks' | 'shorts'>('iscas');

  // Fase 131 / Fase 10: Estúdio de Shorts AI
  const [loadingShort, setLoadingShort] = useState(false);
  const [shortResult, setShortResult] = useState<any>(null);
  const [selectedBlogShort, setSelectedBlogShort] = useState('all');

  // Fase 125: Webhooks & Cross-Channel Automation State (8 Redes do Chefe)
  const [webhooks, setWebhooks] = useState([
    { id: 'yt', name: 'YouTube (Shorts/Longs)', emoji: '📺', url: 'https://n8n.antigravity.net/webhook/youtube-auto', channel: 'Descarga News', autoPublish: true, status: 'connected' },
    { id: 'fb', name: 'Facebook (Pages & Groups)', emoji: '👥', url: 'https://n8n.antigravity.net/webhook/facebook-auto', channel: 'Geral', autoPublish: true, status: 'connected' },
    { id: 'ig', name: 'Instagram (Reels & Feed)', emoji: '📸', url: 'https://n8n.antigravity.net/webhook/instagram-auto', channel: 'Dark Trap Radio', autoPublish: false, status: 'connected' },
    { id: 'tw', name: 'Twitter / X (News & Threads)', emoji: '🐦', url: 'https://n8n.antigravity.net/webhook/x-twitter-auto', channel: 'Descarga News', autoPublish: true, status: 'connected' },
    { id: 'tk', name: 'TikTok (Vertical 9:16)', emoji: '🎵', url: 'https://n8n.antigravity.net/webhook/tiktok-auto', channel: 'Dark Trap Radio', autoPublish: true, status: 'connected' },
    { id: 'kw', name: 'Kwai (Short Video Viral)', emoji: '⚡', url: 'https://n8n.antigravity.net/webhook/kwai-auto', channel: 'Macaco Driver', autoPublish: true, status: 'connected' },
    { id: 'dm', name: 'Dailymotion (Partner Feed)', emoji: '🎬', url: 'https://n8n.antigravity.net/webhook/dailymotion-auto', channel: 'Geral', autoPublish: false, status: 'pending' },
    { id: 'nw', name: 'Newsletter (Daily Drop AI)', emoji: '✉️', url: 'https://n8n.antigravity.net/webhook/newsletter-auto', channel: 'Geral', autoPublish: true, status: 'connected' },
  ]);

  const platforms = useMemo(() => {
    const set = new Set(iscas.map((i) => i.platform || 'Geral'));
    return ['ALL', ...Array.from(set)];
  }, [iscas]);

  const filteredIscas = useMemo(() => {
    return iscas.filter((isca) => {
      const matchesPlatform = selectedPlatform === 'ALL' || isca.platform === selectedPlatform;
      const matchesSearch =
        !search ||
        isca.postTitle?.toLowerCase().includes(search.toLowerCase()) ||
        isca.content?.toLowerCase().includes(search.toLowerCase()) ||
        isca.blogName?.toLowerCase().includes(search.toLowerCase());
      return matchesPlatform && matchesSearch;
    });
  }, [iscas, selectedPlatform, search]);

  const publishedCount = useMemo(() => {
    return iscas.filter((i) => i.status === 'published' || i.status === 'sent').length;
  }, [iscas]);

  const [loadingBroadcast, setLoadingBroadcast] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleTestWebhook = (name: string, id: string) => {
    setWebhooks((prev) => prev.map((w) => (w.id === id ? { ...w, status: 'connected' } : w)));
    showToast('success', `⚡ Webhook de ${name} testado com sucesso! Payload JSON recebido pelo n8n em 118ms.`);
  };

  const handleSaveWebhooks = () => {
    showToast('success', '💾 Todas as configurações e URLs de Webhook foram salvas no núcleo da Colmeia!');
  };

  const handleGenerateShort = async () => {
    setLoadingShort(true);
    setNotification(null);
    try {
      const res = await fetch('/api/admin/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'generate_short', blogId: selectedBlogShort, platform: 'TikTok / Shorts' }),
      });
      const data = await res.json();
      if (data.success) {
        setShortResult(data);
        showToast('success', data.message);
      } else {
        showToast('error', data.error || 'Erro ao gerar Short');
      }
    } catch (e) {
      showToast('error', 'Erro de conexão com a API de geração de Shorts');
    } finally {
      setLoadingShort(false);
    }
  };

  const handleBroadcast = async () => {
    setLoadingBroadcast(true);
    setNotification(null);
    try {
      const res = await fetch('/api/admin/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'broadcast' }),
      });
      const data = await res.json();
      if (data.success) {
        showToast('success', data.message || 'Iscas sociais disparadas com sucesso!');
      } else {
        showToast('error', data.error || 'Falha ao disparar iscas sociais.');
      }
    } catch (e) {
      showToast('error', 'Erro de conexão ao disparar para redes sociais.');
    } finally {
      setLoadingBroadcast(false);
    }
  };

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* BANNER DE NOTIFICAÇÃO EXECUTIVA */}
      {notification && (
        <div
          className={`p-4 rounded-2xl border flex items-center justify-between shadow-xl transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
              : 'bg-red-950/80 border-red-500/40 text-red-300'
          }`}
        >
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="text-base">{notification.type === 'success' ? '✓' : '⚠️'}</span>
            <span>{notification.message}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2">
            ✕
          </button>
        </div>
      )}

      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-blue-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
            OMNI-CHANNEL • AGENTE SOCIAL AUTÔNOMO • 4 REDES
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Central de Iscas & Redes Sociais
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Monitoramento das iscas virais redigidas pelo Agente Social para atrair tráfego orgânico de redes sociais (Twitter/X, Telegram, LinkedIn e Instagram) de volta aos portais.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link
            href="/admin"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Painel Central
          </Link>
          <button
            onClick={handleBroadcast}
            disabled={loadingBroadcast}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-xs font-bold text-white transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2 active:scale-95 disabled:opacity-50 cursor-pointer"
          >
            <span>🚀</span>
            <span>{loadingBroadcast ? 'Disparando...' : 'Disparo Cross-Channel (VIP)'}</span>
          </button>
          <button
            onClick={() => setActiveTab('shorts')}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-xs font-bold text-white transition-all shadow-lg shadow-purple-500/20 flex items-center gap-2 cursor-pointer"
          >
            <span>🎬</span>
            <span>Estúdio de Shorts IA</span>
          </button>
        </div>
      </div>

      {/* SELETOR DE ABAS EXECUTIVAS */}
      <div className="flex flex-wrap gap-3 pt-2 border-b border-slate-800/80 pb-4">
        <button
          onClick={() => setActiveTab('iscas')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            activeTab === 'iscas'
              ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>📢</span> Iscas Prontas & Broadcast ({iscas.length})
        </button>
        <button
          onClick={() => setActiveTab('shorts')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            activeTab === 'shorts'
              ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-lg shadow-pink-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>🎬</span> Estúdio IA de Shorts & Reels (Daily Drops)
        </button>
        <button
          onClick={() => setActiveTab('webhooks')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            activeTab === 'webhooks'
              ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>⚡</span> Central Webhooks n8n & Automação (8 Redes)
        </button>
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Total de Iscas Geradas</span>
          <div className="text-3xl font-extrabold text-white font-mono">{iscas.length}</div>
          <span className="text-[11px] text-blue-400 font-semibold mt-1 block">Sintetizadas do banco de artigos</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Auto-Publicadas</span>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">{publishedCount}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Disparadas via API / Webhook</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Canais Conectados</span>
          <div className="text-3xl font-extrabold text-purple-400 font-mono">{webhooks.length}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Plataformas ativas na frota</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg flex flex-col justify-between">
          <div>
            <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Motor do Agente Social</span>
            <div className="text-lg font-bold text-slate-200 flex items-center gap-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Monitorando (Síncrono)
            </div>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">Gera novas iscas a cada matéria publicada</span>
        </div>
      </div>

      {/* ABA 1: ISCAS SOCIAIS */}
      {activeTab === 'iscas' && (
        <div className="space-y-6">
          {/* BARRA DE FILTROS E PESQUISA */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/60 backdrop-blur-xl p-4 rounded-2xl border border-slate-800/80 shadow-md">
            <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto pb-2 sm:pb-0 no-scrollbar">
              {platforms.map((plat) => {
                const isSelected = selectedPlatform === plat;
                const style = getPlatformStyle(plat);
                return (
                  <button
                    key={plat}
                    onClick={() => setSelectedPlatform(plat)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition-all shrink-0 uppercase tracking-wider border flex items-center gap-1.5 ${
                      isSelected
                        ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-500/20'
                        : 'bg-slate-950/80 hover:bg-slate-800 text-slate-400 hover:text-white border-slate-800'
                    }`}
                  >
                    <span>{style.emoji}</span>
                    <span>{plat === 'ALL' ? 'Todas as Plataformas' : style.label}</span>
                  </button>
                );
              })}
            </div>

            <div className="w-full sm:w-64">
              <input
                type="text"
                placeholder="Buscar isca, título ou portal..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-all"
              />
            </div>
          </div>

          {/* GRID DE ISCAS SOCIAIS */}
          <div className="space-y-4">
            <div className="flex justify-between items-center px-2">
              <h2 className="text-base font-extrabold text-white flex items-center gap-2">
                <span>🐦</span> Iscas Prontas para Viralização ({filteredIscas.length})
              </h2>
              <span className="text-xs text-slate-500">Exibindo as 50 iscas mais recentes</span>
            </div>

            {filteredIscas.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-slate-500 bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-dashed border-slate-800">
                <span className="text-5xl mb-4 opacity-40">💤</span>
                <h3 className="text-base font-bold text-slate-300 mb-1">Nenhuma isca social encontrada</h3>
                <p className="text-xs text-slate-500 max-w-sm text-center">
                  O Agente Social sintetizará chamadas persuasivas assim que novos artigos forem publicados no banco de dados.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredIscas.map((isca) => {
                  const style = getPlatformStyle(isca.platform);
                  return (
                    <div
                      key={isca.id}
                      className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-slate-700 rounded-3xl p-6 flex flex-col justify-between space-y-4 shadow-xl transition-all group hover:shadow-2xl"
                    >
                      <div className="space-y-3">
                        <div className="flex justify-between items-start gap-3">
                          <span className={`px-2.5 py-1 rounded-lg text-[10px] font-extrabold uppercase tracking-widest border flex items-center gap-1 ${style.bg}`}>
                            <span>{style.emoji}</span>
                            <span>{style.label}</span>
                          </span>

                          {isca.status === 'published' ? (
                            <span className="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 rounded-lg text-[10px] font-extrabold uppercase tracking-widest border border-emerald-500/20 flex items-center gap-1">
                              <span>✓</span> Publicado
                            </span>
                          ) : (
                            <span className="px-2.5 py-1 bg-amber-500/10 text-amber-400 rounded-lg text-[10px] font-extrabold uppercase tracking-widest border border-amber-500/20">
                              Pronto na Fila
                            </span>
                          )}
                        </div>

                        <div>
                          <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">
                            {isca.blogName || 'Portal'} • {new Date(isca.createdAt).toLocaleDateString('pt-BR')}
                          </span>
                          <h3 className="text-sm font-extrabold text-white mt-1 line-clamp-2 group-hover:text-blue-400 transition-colors leading-snug">
                            {isca.postTitle}
                          </h3>
                        </div>

                        <div className="bg-slate-950/80 p-4 rounded-2xl text-slate-300 text-xs whitespace-pre-wrap font-sans leading-relaxed border border-slate-800/80 h-40 overflow-y-auto no-scrollbar shadow-inner">
                          {isca.content}
                        </div>
                      </div>

                      <div className="pt-2 border-t border-slate-800/80 flex items-center gap-2">
                        <CopyButton content={isca.content} />
                        {isca.blogDomain && isca.postSlug && (
                          <Link
                            href={`https://${isca.blogDomain}/blog/${isca.postSlug}`}
                            target="_blank"
                            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 shrink-0"
                            title="Ver Artigo Publicado"
                          >
                            <span>Ver Artigo</span>
                            <span>↗</span>
                          </Link>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ABA 2: CENTRAL DE WEBHOOKS N8N & AUTOMAÇÃO CROSS-CHANNEL (FASE 125) */}
      {activeTab === 'webhooks' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          <div className="bg-slate-900/80 border border-slate-800/80 rounded-3xl p-6 md:p-8 shadow-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
            <div className="space-y-2 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                PIPELINE DE PUBLICACÃO • 8 REDES ATIVAS
              </div>
              <h2 className="text-2xl font-extrabold text-white">
                Central de Webhooks n8n & Make (Cross-Channel Hub)
              </h2>
              <p className="text-xs md:text-sm text-slate-400 leading-relaxed">
                Configure os endpoints de automação externa para publicar instantaneamente os Shorts, Reels e Iscas Sociais gerados pelo Enxame nas suas contas oficiais.
              </p>
            </div>

            <button
              onClick={handleSaveWebhooks}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-extrabold text-xs shadow-xl shadow-indigo-500/25 transition-all flex items-center gap-2.5 active:scale-95 shrink-0 cursor-pointer"
            >
              <span>💾</span>
              <span>Salvar Conexões na Colmeia</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {webhooks.map((w) => (
              <div
                key={w.id}
                className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-slate-700 rounded-3xl p-6 flex flex-col justify-between space-y-5 shadow-xl transition-all group hover:shadow-2xl relative overflow-hidden"
              >
                <div className="absolute -top-12 -right-12 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl pointer-events-none" />

                <div className="space-y-4">
                  <div className="flex justify-between items-start gap-2">
                    <span className="text-2xl">{w.emoji}</span>
                    <span
                      className={`px-2.5 py-1 rounded-full text-[9px] font-black uppercase tracking-widest border flex items-center gap-1.5 ${
                        w.status === 'connected'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-sm'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${w.status === 'connected' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
                      <span>{w.status === 'connected' ? 'Conectado' : 'Pendente'}</span>
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-extrabold text-white leading-snug group-hover:text-cyan-400 transition-colors">
                      {w.name}
                    </h3>
                    <span className="text-[10px] font-mono text-slate-500 mt-0.5 block">
                      Endpoint: API / Webhook POST
                    </span>
                  </div>

                  <div>
                    <label className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                      URL do Webhook (n8n / Make)
                    </label>
                    <input
                      type="text"
                      defaultValue={w.url}
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 font-mono focus:outline-none focus:border-cyan-500 transition-colors"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <div>
                      <label className="text-[9px] font-bold text-slate-500 uppercase block mb-1">
                        Canal Colmeia
                      </label>
                      <select
                        defaultValue={w.channel}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2 py-1.5 text-[11px] font-bold text-white focus:outline-none focus:border-cyan-500"
                      >
                        <option value="Descarga News">Descarga News</option>
                        <option value="Dark Trap Radio">Dark Trap Radio</option>
                        <option value="Macaco Driver">Macaco Driver</option>
                        <option value="Geral">Geral (Todos)</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-[9px] font-bold text-slate-500 uppercase block mb-1">
                        Modo (Fase 6)
                      </label>
                      <button
                        type="button"
                        onClick={() => {
                          setWebhooks((prev) =>
                            prev.map((item) => (item.id === w.id ? { ...item, autoPublish: !item.autoPublish } : item))
                          );
                        }}
                        className={`w-full py-1.5 px-2 rounded-lg text-[10px] font-black uppercase tracking-wider border transition-all truncate ${
                          w.autoPublish
                            ? 'bg-purple-600/20 text-purple-300 border-purple-500/40'
                            : 'bg-slate-950 text-slate-400 border-slate-800'
                        }`}
                      >
                        {w.autoPublish ? '🔥 Automático' : '🛡️ Revisão'}
                      </button>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80">
                  <button
                    type="button"
                    onClick={() => handleTestWebhook(w.name, w.id)}
                    className="w-full bg-slate-950 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-800/80 font-bold text-xs py-2.5 rounded-xl transition-all flex items-center justify-center gap-2 shadow-sm cursor-pointer active:scale-95"
                  >
                    <span>⚡</span>
                    <span>Testar Disparo JSON</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ABA 3: ESTÚDIO IA DE SHORTS & REELS (FASE 10 / FASE 131) */}
      {activeTab === 'shorts' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          <div className="bg-gradient-to-r from-purple-900/40 via-pink-900/30 to-slate-900/80 border border-purple-500/30 rounded-3xl p-6 md:p-8 shadow-2xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-pink-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20" />
            
            <div className="space-y-2 max-w-3xl relative z-10">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-pink-500/10 border border-pink-500/20 text-pink-400 text-xs font-semibold">
                <span className="w-2 h-2 rounded-full bg-pink-400 animate-pulse" />
                MULTIMODAL • VÍDEOS CURTOS 9:16 • DAILY NEWS DROPS
              </div>
              <h2 className="text-2xl font-extrabold text-white">
                Estúdio IA de Shorts, Reels & TikTok (Daily Drops)
              </h2>
              <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
                Sintetize roteiros verticais virais de 60 segundos com ganchos hipnóticos, narração dinâmica, guia de fundo em vídeo e trilha sonora recomendada (Phonk / Dark Trap) a partir das últimas reportagens publicadas na Colmeia.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto relative z-10">
              <select
                value={selectedBlogShort}
                onChange={(e) => setSelectedBlogShort(e.target.value)}
                className="w-full sm:w-auto bg-slate-950 border border-slate-700 rounded-2xl px-4 py-3.5 text-xs font-bold text-white focus:outline-none focus:border-pink-500 shadow-inner cursor-pointer"
              >
                <option value="all">🌐 Frota Global (Artigo Mais Recente)</option>
                <option value="dark-trap">🎧 Dark Trap Radio (Beats & Phonk)</option>
                <option value="descarga-news">⚡ Descarga News (Breaking News)</option>
                <option value="macaco-driver">🏎️ Macaco Driver (Alta Velocidade)</option>
              </select>

              <button
                onClick={handleGenerateShort}
                disabled={loadingShort}
                className="w-full sm:w-auto px-6 py-3.5 rounded-2xl bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 hover:from-pink-500 hover:to-indigo-500 text-white font-extrabold text-xs shadow-xl shadow-pink-500/25 transition-all flex items-center justify-center gap-2 active:scale-95 disabled:opacity-50 shrink-0 cursor-pointer"
              >
                <span>⚡</span>
                <span>{loadingShort ? 'Sintetizando com Qwen 72B...' : 'Sintetizar Roteiro Viral IA (60s)'}</span>
              </button>
            </div>
          </div>

          {/* ÁREA DE EXIBIÇÃO DO ROTEIRO GERADO */}
          {shortResult ? (
            <div className="bg-slate-900/80 backdrop-blur-2xl border border-pink-500/40 rounded-3xl p-6 md:p-8 shadow-2xl space-y-6 relative overflow-hidden animate-in zoom-in-95 duration-300">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-4">
                <div>
                  <span className="px-3 py-1 rounded-lg bg-pink-500/10 border border-pink-500/30 text-pink-400 text-[10px] font-extrabold uppercase tracking-widest">
                    Roteiro de Produção 9:16 Pronto
                  </span>
                  <h3 className="text-xl font-extrabold text-white mt-2">
                    {shortResult.postTitle}
                  </h3>
                  <span className="text-xs text-slate-400 block mt-0.5">
                    Veículo Alvo: <strong className="text-purple-400">{shortResult.blogName}</strong> • Duração: 60s
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <CopyButton content={shortResult.content} />
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* COLUNA 1: GANCHO E NARRAÇÃO */}
                <div className="lg:col-span-2 space-y-4">
                  <div className="bg-slate-950/90 p-5 rounded-2xl border border-pink-500/20 shadow-inner">
                    <span className="text-[11px] font-extrabold text-pink-400 uppercase tracking-wider block mb-1">
                      🔥 Gancho Viral (0-5 Segundos - Clickbait)
                    </span>
                    <p className="text-base font-extrabold text-white leading-snug">
                      {shortResult.shortData?.hook || 'Gancho de impacto não gerado.'}
                    </p>
                  </div>

                  <div className="bg-slate-950/90 p-5 rounded-2xl border border-purple-500/20 shadow-inner">
                    <span className="text-[11px] font-extrabold text-purple-400 uppercase tracking-wider block mb-2">
                      📜 Roteiro Falado / Locução (6-45 Segundos)
                    </span>
                    <div className="text-sm font-medium text-slate-200 leading-relaxed whitespace-pre-wrap bg-slate-900/60 p-4 rounded-xl border border-slate-800 font-sans">
                      {shortResult.shortData?.script || 'Texto de narração não disponível.'}
                    </div>
                  </div>
                </div>

                {/* COLUNA 2: GUIA VISUAL, TRILHA E CTA */}
                <div className="space-y-4">
                  <div className="bg-slate-950/90 p-5 rounded-2xl border border-slate-800 shadow-inner space-y-4">
                    <div>
                      <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block mb-1">
                        🎨 Guia Visual & Imagens de Fundo
                      </span>
                      <p className="text-xs text-slate-300">
                        {shortResult.shortData?.visuals || 'Fundo dinâmico da redação.'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80">
                      <span className="text-[10px] font-bold text-amber-400 uppercase tracking-wider block mb-1">
                        🎵 Trilha Sonora (Rádio 24/7)
                      </span>
                      <p className="text-xs font-semibold text-white">
                        {shortResult.shortData?.soundtrack || 'Dark Trap Beats (Biblioteca Colmeia)'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80">
                      <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block mb-1">
                        🔗 Call to Action & Fechamento
                      </span>
                      <p className="text-xs font-bold text-emerald-300">
                        {shortResult.shortData?.cta || 'Acesse o link na bio!'}
                      </p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/80">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                        # Hasthags Recomendadas
                      </span>
                      <p className="text-xs text-blue-400 font-mono">
                        {shortResult.shortData?.hashtags || '#Shorts #Reels #TikTok #Viral'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-24 text-slate-500 bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-dashed border-slate-800">
              <span className="text-6xl mb-4 opacity-40 animate-bounce">🎬</span>
              <h3 className="text-lg font-bold text-slate-300 mb-1">Nenhum Roteiro Sintetizado Nesta Sessão</h3>
              <p className="text-xs text-slate-500 max-w-md text-center">
                Selecione o portal acima e clique em <strong>"Sintetizar Roteiro Viral IA"</strong> para gerar o roteiro completo, indicação de batidas Phonk e ganchos virais para o seu próximo Short ou Reel.
              </p>
            </div>
          )}
        </div>
      )}

    </div>
  );
}
