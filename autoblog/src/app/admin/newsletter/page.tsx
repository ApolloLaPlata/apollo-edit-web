'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface CampaignItem {
  id: string;
  blogId: string;
  blogName?: string;
  blogDomain?: string;
  subject: string;
  contentHtml: string;
  sentCount: number;
  createdAt: string;
}

interface NewsletterStats {
  totalCampaigns: number;
  totalSentCount: number;
  totalLeadsInBase: number;
  totalAffiliatesAvailable: number;
}

export default function NewsletterStudio() {
  const [loading, setLoading] = useState(false);
  const [htmlContent, setHtmlContent] = useState('');
  const [subject, setSubject] = useState('');
  const [selectedBlog, setSelectedBlog] = useState('all');
  const [stats, setStats] = useState<NewsletterStats | null>(null);
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string; testUrl?: string } | null>(null);
  const [previewingCampaign, setPreviewingCampaign] = useState<CampaignItem | null>(null);

  const showToast = (type: 'success' | 'error' | 'info', message: string, testUrl?: string) => {
    setNotification({ type, message, testUrl });
    setTimeout(() => setNotification(null), 8000);
  };

  const fetchHistoryAndStats = async () => {
    try {
      const url = selectedBlog !== 'all' ? `/api/admin/newsletter?blogId=${selectedBlog}` : '/api/admin/newsletter';
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          setStats(data.stats);
          setCampaigns(data.campaigns || []);
        }
      }
    } catch (err) {
      console.error('Erro ao buscar telemetria da newsletter:', err);
    }
  };

  useEffect(() => {
    fetchHistoryAndStats();
  }, [selectedBlog]);

  const generateNewsletter = async () => {
    setLoading(true);
    setHtmlContent('');
    setSubject('');
    setNotification(null);

    try {
      const res = await fetch('/api/admin/newsletter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blogId: selectedBlog })
      });
      const data = await res.json();
      
      if (data.success) {
        setSubject(data.subject);
        setHtmlContent(data.html);
        showToast('success', `Newsletter gerada pelo Carteiro Neural (${data.blogName}) com ofertas de afiliados acopladas!`);
      } else {
        showToast('error', data.error || 'Falha ao redigir newsletter.');
      }
    } catch (err) {
      showToast('error', 'Erro de conexão ao comunicar com o Carteiro Neural.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyHTML = () => {
    if (!htmlContent) return;
    navigator.clipboard.writeText(htmlContent);
    showToast('info', 'Código HTML copiado para a área de transferência!');
  };

  const handleBroadcast = async () => {
    if (!htmlContent || !subject) {
      showToast('error', 'Preencha o Assunto e gere o HTML antes do disparo.');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/admin/newsletter', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          blogId: selectedBlog,
          subject,
          html: htmlContent
        })
      });
      const data = await res.json();
      if (data.success) {
        showToast('success', data.message, data.testUrl || undefined);
        fetchHistoryAndStats(); // Atualizar histórico no painel
      } else {
        showToast('error', data.error || 'Falha ao processar disparo em massa.');
      }
    } catch (err) {
      showToast('error', 'Erro de conexão com o servidor de disparo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500 font-sans">
      
      {/* BANNER DE NOTIFICAÇÃO EXECUTIVA */}
      {notification && (
        <div
          className={`p-4 rounded-2xl border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : notification.type === 'error'
              ? 'bg-red-950/90 border-red-500/50 text-red-300'
              : 'bg-blue-950/90 border-blue-500/50 text-blue-300'
          }`}
        >
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="text-base">
              {notification.type === 'success' ? '🚀' : notification.type === 'error' ? '⚠️' : 'ℹ️'}
            </span>
            <span>{notification.message}</span>
            {notification.testUrl && (
              <a
                href={notification.testUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 bg-emerald-500 text-black px-2.5 py-1 rounded-lg font-extrabold hover:bg-emerald-400 transition-all underline ml-2"
              >
                👉 Ver E-mail Enviado no Ethereal
              </a>
            )}
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2 self-end md:self-center">
            ✕
          </button>
        </div>
      )}

      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-orange-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
            FASE 9 DO PIPELINE • CARTEIRO NEURAL 2.0 & MONETIZAÇÃO VIP
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Estúdio de E-mail & Newsletter Afiliada
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Invoque a IA para sintetizar as notícias e inserir automaticamente ofertas de afiliados verificadas no corpo do e-mail. Dispare para a base VIP com auditoria no SQLite.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link
            href="/admin/leads"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Base de Leads VIP
          </Link>
          <button
            onClick={generateNewsletter}
            disabled={loading}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-500 hover:to-amber-500 text-xs font-extrabold text-white transition-all shadow-lg shadow-orange-500/20 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none flex items-center gap-2.5"
          >
            {loading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <span>⚡</span>
            )}
            <span>{loading ? 'Sintetizando Edição...' : 'Gerar Edição da Semana (com Afiliados)'}</span>
          </button>
        </div>
      </div>

      {/* TELEMETRIA EXECUTIVA DO CARTEIRO */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">✉️ Campanhas Enviadas</span>
          <div className="text-3xl font-black text-white">{stats?.totalCampaigns || 0}</div>
          <span className="text-[11px] text-orange-400 font-medium">Edições VIP disparadas na rede</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">📬 E-mails Entregues</span>
          <div className="text-3xl font-black text-emerald-400">{stats?.totalSentCount || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Leitores alcançados na caixa de entrada</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">👥 Leads na Base SQLite</span>
          <div className="text-3xl font-black text-sky-400">{stats?.totalLeadsInBase || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Inscritos elegíveis para disparo</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">🛍️ Afiliados no Inventário</span>
          <div className="text-3xl font-black text-purple-400">{stats?.totalAffiliatesAvailable || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Ofertas prontos para injeção no e-mail</span>
        </div>
      </div>

      {/* SELETOR DE PORTAL PARA FILTRO DE DISPARO */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between bg-slate-900/60 p-5 rounded-2xl border border-slate-800 gap-4">
        <div>
          <h3 className="text-sm font-bold text-white">🌐 Portal Alvo da Campanha</h3>
          <p className="text-xs text-slate-400">Selecione para qual blog da frota você deseja gerar as notícias e disparar os e-mails.</p>
        </div>
        <select
          value={selectedBlog}
          onChange={(e) => setSelectedBlog(e.target.value)}
          className="bg-slate-950 border border-slate-700 text-white text-xs font-bold px-4 py-2.5 rounded-xl outline-none focus:border-orange-500 transition-colors w-full sm:w-auto"
        >
          <option value="all">🌐 Todos os Portais / Frota Global</option>
          <option value="dark-trap">🎵 Dark Trap Radio (Phonk & Trap)</option>
          <option value="descarga-news">📰 Descarga News (Notícias & IA)</option>
          <option value="macaco-driver">🏎️ Macaco Driver (Automotivo)</option>
        </select>
      </div>

      {/* EDITOR VISUAL AO VIVO: TEMPLATES + CÓDIGO EDITÁVEL + PREVIEW */}
      {htmlContent && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

          {/* TOOLBAR DE AÇÕES E ASSUNTO EDITÁVEL */}
          <div className="bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-6 shadow-xl flex flex-col md:flex-row gap-5 items-start md:items-end">
            <div className="flex-1 min-w-0">
              <label className="text-[10px] text-orange-400 uppercase font-bold tracking-wider block mb-1.5">Assunto do E-mail (Editável)</label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-white font-bold text-sm focus:outline-none focus:border-orange-500 transition-colors placeholder-slate-600"
                placeholder="Ex: 🔥 As 5 Notícias que Você Não Pode Perder Esta Semana"
              />
            </div>
            <div className="flex flex-wrap gap-2.5 shrink-0">
              <button
                onClick={handleCopyHTML}
                className="bg-slate-950 hover:bg-slate-800 px-4 py-3 rounded-xl text-slate-300 hover:text-white font-bold transition-all text-xs border border-slate-700/80 shadow-sm flex items-center gap-1.5 active:scale-95"
              >
                <span>📋</span><span>Copiar HTML</span>
              </button>
              <button
                onClick={handleBroadcast}
                disabled={loading}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 px-6 py-3 rounded-xl text-white font-extrabold transition-all text-xs border border-emerald-500/30 shadow-md shadow-emerald-500/20 flex items-center gap-2 active:scale-95 disabled:opacity-50"
              >
                <span>🚀</span><span>Disparo em Massa (Base VIP)</span>
              </button>
            </div>
          </div>

          {/* EDITOR SPLIT: CÓDIGO EDITÁVEL (LEFT) + PREVIEW AO VIVO (RIGHT) */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* EDITOR DE CÓDIGO */}
            <div className="bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-slate-800/80 overflow-hidden flex flex-col h-[680px] shadow-2xl">
              <div className="bg-slate-950/80 px-5 py-3.5 border-b border-slate-800 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-orange-400 animate-pulse" />
                  <span className="text-slate-300 font-bold text-xs uppercase tracking-wider">Editor HTML (Código Editável)</span>
                </div>
                <span className="text-[10px] text-slate-500 font-mono">Linha 1 · {htmlContent.length} chars</span>
              </div>
              <textarea
                value={htmlContent}
                onChange={(e) => setHtmlContent(e.target.value)}
                className="flex-1 w-full bg-slate-950/60 resize-none p-5 text-[11px] text-cyan-300 font-mono leading-relaxed focus:outline-none border-0 placeholder-slate-700"
                spellCheck={false}
                placeholder="Cole ou edite o HTML da newsletter aqui..."
              />
              <div className="bg-slate-950/80 px-5 py-2.5 border-t border-slate-800 flex justify-between items-center text-[10px] font-mono text-slate-600">
                <span>Edição 100% responsiva em Inline CSS</span>
                <span className="text-emerald-400 font-bold">• Preview sincronizado ao vivo →</span>
              </div>
            </div>

            {/* PREVIEW AO VIVO */}
            <div className="bg-white rounded-3xl border-4 border-slate-800 overflow-hidden flex flex-col h-[680px] shadow-2xl relative">
              <div className="bg-slate-100 px-5 py-3.5 border-b border-slate-200 flex justify-between items-center">
                <span className="text-slate-800 font-extrabold text-xs tracking-wider uppercase">📬 Preview Ao Vivo (Caixa de Entrada do Leitor)</span>
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-400/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-400/80" />
                </div>
              </div>
              <div
                className="flex-1 p-8 overflow-y-auto font-sans text-slate-900 prose prose-sm max-w-none text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
              />
            </div>
          </div>
        </div>
      )}

      {/* ESTADO VAZIO */}
      {!htmlContent && !loading && (
        <div className="py-20 text-center text-slate-500 bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-dashed border-slate-800 flex flex-col items-center justify-center p-8">
          <div className="w-16 h-16 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-4xl mb-4">
            ✉️
          </div>
          <h2 className="text-base font-bold text-slate-200 mb-1">Estúdio de E-mail aguardando injeção neural</h2>
          <p className="text-xs text-slate-500 max-w-md">
            Clique em &quot;Gerar Edição da Semana (com Afiliados)&quot; no topo para o Qwen 72B analisar os últimos artigos do portal selecionado e montar o e-mail VIP com recomendações de compra.
          </p>
        </div>
      )}

      {/* HISTÓRICO DE AUDITORIA DE CAMPANHAS (SQLITE) */}
      <div className="bg-slate-900/60 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>🗄️ Auditoria de Campanhas Enviadas (`NewsletterCampaign`)</span>
              <span className="text-xs bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full font-mono">
                {campaigns.length} registros
              </span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Histórico imutável de disparos realizados para as listas VIP do ecossistema</p>
          </div>
          <button
            onClick={fetchHistoryAndStats}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 transition-all"
          >
            🔄 Sincronizar Histórico
          </button>
        </div>

        {campaigns.length === 0 ? (
          <div className="py-12 text-center text-slate-500 font-mono text-xs">Nenhuma campanha registrada no banco até o momento.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Assunto & Portal</th>
                  <th className="py-3 px-4">Destinatários</th>
                  <th className="py-3 px-4">Data do Disparo</th>
                  <th className="py-3 px-4 text-right">Auditoria</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs">
                {campaigns.map((c) => (
                  <tr key={c.id} className="hover:bg-slate-800/30 transition-all">
                    <td className="py-3 px-4">
                      <div className="font-bold text-white text-sm leading-tight">{c.subject}</div>
                      <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                        🌐 {c.blogName || (c.blogId === 'global' ? 'Frota Global Colmeia' : c.blogId)}
                      </div>
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-emerald-400">
                      <span>📬 {c.sentCount} leads alcançados</span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(c.createdAt).toLocaleDateString('pt-BR')} às {new Date(c.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => setPreviewingCampaign(c)}
                        className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold transition-all inline-flex items-center gap-1.5"
                      >
                        <span>👁️</span> <span>Ver HTML Enviado</span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* MODAL DE PREVIEW DE CAMPANHA ANTIGA */}
      {previewingCampaign && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-700 rounded-3xl w-full max-w-3xl h-[80vh] flex flex-col shadow-2xl overflow-hidden">
            <div className="bg-slate-950 p-4 border-b border-slate-800 flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-white">{previewingCampaign.subject}</h3>
                <span className="text-[11px] text-slate-400 font-mono">Disparado para {previewingCampaign.sentCount} leads em {new Date(previewingCampaign.createdAt).toLocaleDateString('pt-BR')}</span>
              </div>
              <button
                onClick={() => setPreviewingCampaign(null)}
                className="w-8 h-8 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold flex items-center justify-center"
              >
                ✕
              </button>
            </div>
            <div className="flex-1 bg-white p-6 overflow-y-auto">
              <div
                className="font-sans text-slate-900 prose prose-sm max-w-none text-sm leading-relaxed"
                dangerouslySetInnerHTML={{ __html: previewingCampaign.contentHtml }}
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
