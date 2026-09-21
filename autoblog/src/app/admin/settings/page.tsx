'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

interface BlogSimple {
  id: string;
  name: string;
  domain: string;
  theme?: string;
}

export default function SettingsPage() {
  const [blogId, setBlogId] = useState<string | null>(null);
  const [allBlogs, setAllBlogs] = useState<BlogSimple[]>([]);
  
  const [localMemory, setLocalMemory] = useState('');
  const [youtubeChannelId, setYoutubeChannelId] = useState('');
  const [instagramHandle, setInstagramHandle] = useState('');
  const [twitterHandle, setTwitterHandle] = useState('');
  const [rssSniperUrl, setRssSniperUrl] = useState('');
  const [telegramBotToken, setTelegramBotToken] = useState('');
  const [telegramChatId, setTelegramChatId] = useState('');
  const [discordWebhookUrl, setDiscordWebhookUrl] = useState('');
  const [whatsappApiUrl, setWhatsappApiUrl] = useState('');
  const [whatsappGroupId, setWhatsappGroupId] = useState('');
  const [postIntervalHours, setPostIntervalHours] = useState(4);
  const [isActive, setIsActive] = useState(false);
  
  const [primaryColor, setPrimaryColor] = useState('#06b6d4');
  const [secondaryColor, setSecondaryColor] = useState('#3b82f6');
  const [layoutStyle, setLayoutStyle] = useState('modern');

  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testingWebhooks, setTestingWebhooks] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  useEffect(() => {
    const saved = localStorage.getItem('apollo_active_workspace');
    if (saved && saved !== 'global') {
      setBlogId(saved);
    } else {
      setBlogId(null);
    }
    fetchAllBlogs();
  }, []);

  useEffect(() => {
    if (blogId) fetchConfigs(blogId);
  }, [blogId]);

  const fetchAllBlogs = async () => {
    try {
      const res = await fetch('/api/admin/blogs');
      const data = await res.json();
      if (data.success && data.blogs) {
        setAllBlogs(data.blogs);
      }
    } catch (e) {
      console.error('Erro ao buscar lista de portais:', e);
    }
  };

  const fetchConfigs = async (id: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/settings?blogId=${id}`);
      const data = await res.json();
      if (data.success && data.config) {
        setLocalMemory(data.config.localMemory || '');
        setYoutubeChannelId(data.config.youtubeChannelId || '');
        setInstagramHandle(data.config.instagramHandle || '');
        setTwitterHandle(data.config.twitterHandle || '');
        setRssSniperUrl(data.config.rssSniperUrl || '');
        setTelegramBotToken(data.config.telegramBotToken || '');
        setTelegramChatId(data.config.telegramChatId || '');
        setDiscordWebhookUrl(data.config.discordWebhookUrl || '');
        setWhatsappApiUrl(data.config.whatsappApiUrl || '');
        setWhatsappGroupId(data.config.whatsappGroupId || '');
        setPostIntervalHours(data.config.postIntervalHours ?? 4);
        setIsActive(data.config.isActive === 1);
        setPrimaryColor(data.config.primaryColor || '#06b6d4');
        setSecondaryColor(data.config.secondaryColor || '#3b82f6');
        setLayoutStyle(data.config.layoutStyle || 'modern');
      } else {
        setLocalMemory('');
        setYoutubeChannelId('');
        setInstagramHandle('');
        setTwitterHandle('');
        setRssSniperUrl('');
        setTelegramBotToken('');
        setTelegramChatId('');
        setDiscordWebhookUrl('');
        setWhatsappApiUrl('');
        setWhatsappGroupId('');
        setPostIntervalHours(4);
        setIsActive(false);
        setPrimaryColor('#06b6d4');
        setSecondaryColor('#3b82f6');
        setLayoutStyle('modern');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTestWebhooks = async () => {
    setTestingWebhooks(true);
    setNotification(null);
    try {
      const res = await fetch('/api/admin/social', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'test_webhooks', blogId }),
      });
      const data = await res.json();
      if (data.success) {
        showToast('success', data.message || '⚡ Ping de teste disparado para os Webhooks com status 200 OK!');
      } else {
        showToast('error', data.error || 'Falha ao testar Webhooks.');
      }
    } catch (e) {
      showToast('error', 'Erro de conexão ao testar Webhooks.');
    } finally {
      setTestingWebhooks(false);
    }
  };

  const handleSave = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setSaving(true);
    setNotification(null);
    try {
      const res = await fetch('/api/admin/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          blogId,
          localMemory,
          youtubeChannelId,
          instagramHandle,
          twitterHandle,
          rssSniperUrl,
          telegramBotToken,
          telegramChatId,
          discordWebhookUrl,
          whatsappApiUrl,
          whatsappGroupId,
          postIntervalHours,
          isActive,
          primaryColor,
          secondaryColor,
          layoutStyle,
        }),
      });
      const data = await res.json();
      if (data.success) {
        showToast('success', 'Configurações de Inteligência Artificial e integrações salvas com sucesso no SQLite!');
      } else {
        showToast('error', data.error || 'Falha ao salvar parâmetros no servidor.');
      }
    } catch (err) {
      showToast('error', 'Erro de conexão com o servidor de configurações.');
    } finally {
      setSaving(false);
    }
  };

  const handleSelectPortalFromGlobal = (id: string) => {
    localStorage.setItem('apollo_active_workspace', id);
    setBlogId(id);
    window.dispatchEvent(new Event('storage'));
  };

  if (!blogId) {
    return (
      <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
        <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col items-center text-center">
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-3xl mb-4 text-amber-400">
            ⚙️
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight mb-2">
            Selecione um Veículo para Calibrar o Cérebro Neural
          </h1>
          <p className="text-slate-400 text-xs md:text-sm max-w-lg mb-8 leading-relaxed">
            As diretrizes editoriais, feeds de RSS e chaves de API (Telegram/WhatsApp/Discord) são específicas e isoladas para cada portal da sua rede.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 w-full max-w-4xl">
            {allBlogs.length === 0 ? (
              <div className="col-span-full py-12 text-slate-500 text-xs font-semibold">
                Nenhum portal encontrado no banco de dados.
              </div>
            ) : (
              allBlogs.map((b) => (
                <button
                  key={b.id}
                  onClick={() => handleSelectPortalFromGlobal(b.id)}
                  className="p-6 rounded-2xl bg-slate-950/80 hover:bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition-all text-left flex flex-col justify-between group shadow-lg"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-amber-400 uppercase tracking-widest">Portal ID: {b.id}</span>
                      <span className="text-xs group-hover:translate-x-1 transition-transform">→</span>
                    </div>
                    <h3 className="text-base font-extrabold text-white group-hover:text-amber-400 transition-colors">
                      {b.name}
                    </h3>
                    <span className="text-xs font-mono text-slate-400 mt-1 block">{b.domain}</span>
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-900 flex items-center gap-2 text-[11px] font-bold text-slate-500">
                    <span>⚡</span> Configurar IA & Integrações
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }

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
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-amber-500/10 via-orange-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
            CENTRAL DE INTELIGÊNCIA • CÉREBRO DO VEÍCULO
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Parâmetros Neurais, RSS & Webhooks
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Calibre a personalidade do robô redator, configure canais de extração de notícias via RSS Sniper e conecte bots para alertas no Telegram e WhatsApp.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <button
            onClick={() => {
              localStorage.setItem('apollo_active_workspace', 'global');
              setBlogId(null);
              window.dispatchEvent(new Event('storage'));
            }}
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm"
          >
            ← Trocar Portal
          </button>
          <button
            onClick={handleTestWebhooks}
            disabled={testingWebhooks || loading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/20 hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center gap-2 cursor-pointer"
          >
            <span>⚡</span>
            <span>{testingWebhooks ? 'Testando...' : 'Testar Webhooks'}</span>
          </button>
          <button
            onClick={handleSave}
            disabled={saving || loading}
            className="px-8 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-xs font-extrabold text-white transition-all shadow-lg shadow-orange-500/20 hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center gap-2 cursor-pointer"
          >
            {saving ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <span>💾</span>
            )}
            <span>{saving ? 'Gravando no SQLite...' : 'Salvar Alterações'}</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-24 text-center text-slate-500 text-xs font-semibold animate-pulse">
          Carregando parâmetros do portal...
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* COLUNA 1: MOTOR DE CRIAÇÃO E RSS */}
          <div className="space-y-8">
            
            {/* MOTOR DE REDAÇÃO */}
            <div className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl space-y-6">
              <div className="border-b border-slate-800 pb-4">
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <span>🧠</span> Motor de Redação & Memória Local
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Diretrizes de nicho, estilo de escrita e tom de voz.</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Memória de Nicho & Regras Editoriais (System Prompt)
                </label>
                <textarea
                  rows={6}
                  value={localMemory}
                  onChange={(e) => setLocalMemory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-2xl p-4 text-xs font-mono text-white focus:outline-none focus:border-amber-500 transition-all leading-relaxed"
                  placeholder="Ex: Você é um portal de notícias tech. Redija artigos com parágrafos curtos, subtítulos chamativos e otimizados para alto CPC."
                />
              </div>

              {/* PILOTO AUTOMÁTICO */}
              <div className="bg-slate-950/80 p-5 rounded-2xl border border-slate-800/80 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-extrabold text-white">Piloto Automático (Auto-Post)</h3>
                    <p className="text-xs text-slate-400 mt-0.5">O robô buscará pautas e publicará artigos sem intervenção humana.</p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setIsActive(!isActive)}
                    className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors ${
                      isActive ? 'bg-emerald-500' : 'bg-slate-800'
                    }`}
                  >
                    <span
                      className={`inline-block h-5 w-5 transform rounded-full bg-white transition-transform ${
                        isActive ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>

                <div className="border-t border-slate-900 pt-4">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-300 mb-2">
                    <span>Intervalo Biológico entre Publicações</span>
                    <span className="text-amber-400 font-mono font-black text-sm">{postIntervalHours} horas</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="24"
                    value={postIntervalHours}
                    onChange={(e) => setPostIntervalHours(parseInt(e.target.value))}
                    className="w-full accent-amber-500 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500 font-mono mt-1">
                    <span>Agressivo (1h)</span>
                    <span>Moderado (6h)</span>
                    <span>Diário (24h)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* RSS SNIPER */}
            <div className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl space-y-4">
              <div className="border-b border-slate-800 pb-4">
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <span>📡</span> RSS Sniper & Triggers de Matérias
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Alimente o robô com feeds XML ou URLs de portais de referência.</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  URL do Feed RSS / XML
                </label>
                <input
                  type="text"
                  value={rssSniperUrl}
                  onChange={(e) => setRssSniperUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs font-mono text-white focus:outline-none focus:border-blue-500 transition-all"
                  placeholder="https://feed.g1.globo.com/rss/tecnologia.xml"
                />
              </div>
            </div>

          </div>

          {/* COLUNA 2: REDES SOCIAIS E TELEMETRIA / WEBHOOKS */}
          <div className="space-y-8">
            
            {/* IDENTIDADE SOCIAL */}
            <div className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl space-y-5">
              <div className="border-b border-slate-800 pb-4">
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <span>🌐</span> Identidade Social & Canais
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Associação de perfis para distribuição de iscas e vídeos.</p>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  ID do Canal YouTube Primário
                </label>
                <input
                  type="text"
                  value={youtubeChannelId}
                  onChange={(e) => setYoutubeChannelId(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs font-mono text-white focus:outline-none focus:border-pink-500 transition-all"
                  placeholder="UCxxxxxxxxxxxxxxxxxxxxxx"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Instagram Handle
                  </label>
                  <input
                    type="text"
                    value={instagramHandle}
                    onChange={(e) => setInstagramHandle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-pink-500 transition-all"
                    placeholder="@seucanal"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Twitter / X Handle
                  </label>
                  <input
                    type="text"
                    value={twitterHandle}
                    onChange={(e) => setTwitterHandle(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-pink-500 transition-all"
                    placeholder="@seucanal"
                  />
                </div>
              </div>
            </div>

            {/* WEBHOOKS E ALERTAS OMNI-CHANNEL */}
            <div className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl space-y-5">
              <div className="border-b border-slate-800 pb-4">
                <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                  <span>📲</span> Notificações Push & Webhooks (Infiltrado)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">Receba alertas em tempo real sobre artigos publicados e erros neurais.</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Telegram Bot Token
                  </label>
                  <input
                    type="password"
                    value={telegramBotToken}
                    onChange={(e) => setTelegramBotToken(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-emerald-500 transition-all"
                    placeholder="738291...AAFX_..."
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    Telegram Chat ID
                  </label>
                  <input
                    type="text"
                    value={telegramChatId}
                    onChange={(e) => setTelegramChatId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-emerald-500 transition-all"
                    placeholder="-100123456789"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                  Discord Webhook URL (Redação IA)
                </label>
                <input
                  type="password"
                  value={discordWebhookUrl}
                  onChange={(e) => setDiscordWebhookUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs font-mono text-white focus:outline-none focus:border-emerald-500 transition-all"
                  placeholder="https://discord.com/api/webhooks/..."
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    WhatsApp API URL (Evolution)
                  </label>
                  <input
                    type="text"
                    value={whatsappApiUrl}
                    onChange={(e) => setWhatsappApiUrl(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-emerald-500 transition-all"
                    placeholder="https://sua-evolution-api.com"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
                    WhatsApp Group ID
                  </label>
                  <input
                    type="text"
                    value={whatsappGroupId}
                    onChange={(e) => setWhatsappGroupId(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-emerald-500 transition-all"
                    placeholder="551199999999@g.us"
                  />
                </div>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
