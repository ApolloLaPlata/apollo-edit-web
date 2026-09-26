'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface ConciergeLogItem {
  id: string;
  blogId: string;
  blogName?: string;
  visitorId: string;
  postSlug?: string;
  userMessage: string;
  botReply: string;
  recommendedUrl?: string;
  recommendedKeyword?: string;
  capturedEmail?: string;
  createdAt: string;
}

interface ConciergeStats {
  totalChats: number;
  totalAffiliatesRecommended: number;
  totalLeadsCaptured: number;
  conversionRate: string;
  recentLogs: ConciergeLogItem[];
}

export default function ConciergeDashboard() {
  const [stats, setStats] = useState<ConciergeStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedBlog, setSelectedBlog] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    try {
      const url = selectedBlog ? `/api/admin/concierge?blogId=${selectedBlog}` : '/api/admin/concierge';
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Erro ao buscar estatísticas do concierge:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [selectedBlog]);

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-16 font-sans animate-in fade-in duration-500">
      
      {/* HEADER DO PAINEL */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-96 h-96 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none -mr-32 -mt-32" />
        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            FASE 8 DO PIPELINE • ATENDIMENTO NEURAL & VENDAS EM PORTAIS
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Concierge Neural & Chatbot de Chumbo
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl font-normal leading-relaxed">
            Monitore em tempo real as conversas do assistente interativo embutido nos seus blogs, veja recomendações automáticas de ofertas de afiliados e acompanhe os novos leads VIP capturados.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link href="/admin" className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2">
            ← Painel Central
          </Link>
          <button onClick={fetchStats} className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-extrabold text-white transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2">
            🔄 Sincronizar Telemetria
          </button>
        </div>
      </div>

      {/* TELEMETRIA & KPIS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">💬 Atendimentos Realizados</span>
          <div className="text-3xl font-black text-white">{loading ? '...' : stats?.totalChats || 0}</div>
          <span className="text-[11px] text-indigo-400 font-medium">Interações 24/7 com visitantes</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">🛍️ Ofertas Afiliadas Indicadas</span>
          <div className="text-3xl font-black text-emerald-400">{loading ? '...' : stats?.totalAffiliatesRecommended || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Recomendações cirúrgicas de produtos</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">📬 Leads Capturados via Chat</span>
          <div className="text-3xl font-black text-sky-400">{loading ? '...' : stats?.totalLeadsCaptured || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">E-mails salvos no CRM Neural</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">🎯 Taxa de Conversão (Leads)</span>
          <div className="text-3xl font-black text-purple-400">{loading ? '...' : stats?.conversionRate || '0.0%'}</div>
          <span className="text-[11px] text-slate-400 font-medium">Eficácia de fechamento de leads</span>
        </div>
      </div>

      {/* SELETOR DE PORTAL PARA FILTRO */}
      <div className="flex items-center justify-between bg-slate-900/40 p-4 rounded-2xl border border-slate-800">
        <span className="text-xs font-bold text-slate-300">Filtrar Atendimento por Portal da Rede:</span>
        <select
          value={selectedBlog}
          onChange={(e) => setSelectedBlog(e.target.value)}
          className="bg-slate-950 border border-slate-700 text-white text-xs font-bold px-4 py-2 rounded-xl outline-none focus:border-indigo-500"
        >
          <option value="">🌐 Todos os Portais da Frota</option>
          <option value="dark-trap">🎵 Dark Trap Radio (Phonk & Trap)</option>
          <option value="descarga-news">📰 Descarga News (Notícias & IA)</option>
          <option value="macaco-driver">🏎️ Macaco Driver (Automotivo)</option>
        </select>
      </div>

      {/* FEED AO VIVO DE CONVERSAS & AUDITORIA */}
      <div className="bg-slate-900/60 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>🧠 Auditoria Ao Vivo de Atendimento & Vendas</span>
            <span className="text-xs bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full font-mono">
              {stats?.recentLogs?.length || 0} registros
            </span>
          </h2>
          <span className="text-xs text-emerald-400 font-bold flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            Em tempo real (SQLite)
          </span>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-500 font-mono text-xs">Carregando auditoria neural...</div>
        ) : !stats?.recentLogs || stats.recentLogs.length === 0 ? (
          <div className="py-16 text-center text-slate-500 bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <span className="text-3xl block mb-2">💬</span>
            <h3 className="font-bold text-sm text-slate-300">Nenhum atendimento registrado até o momento</h3>
            <p className="text-xs text-slate-500 mt-1">Quando os leitores interagirem com o balão de chat no front-end dos blogs, as conversas aparecerão aqui.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {stats.recentLogs.map((log) => (
              <div key={log.id} className="bg-slate-950/80 p-5 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition-all space-y-3">
                
                {/* TOPO DO LOG */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/60 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-extrabold text-white bg-indigo-950 text-indigo-300 px-2.5 py-0.5 rounded-lg border border-indigo-800/60">
                      {log.blogName || log.blogId}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">ID: {log.visitorId}</span>
                    {log.postSlug && (
                      <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono truncate max-w-[200px]">
                        📄 /{log.postSlug}
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {log.recommendedKeyword && (
                      <span className="text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800/80 px-2 py-0.5 rounded font-bold flex items-center gap-1">
                        <span>🛍️</span> <span>Afiliado: {log.recommendedKeyword}</span>
                      </span>
                    )}
                    {log.capturedEmail && (
                      <span className="text-[10px] bg-sky-950 text-sky-400 border border-sky-800/80 px-2 py-0.5 rounded font-bold flex items-center gap-1">
                        <span>📬</span> <span>Lead: {log.capturedEmail}</span>
                      </span>
                    )}
                    <span className="text-[10px] text-slate-500 font-mono">
                      {new Date(log.createdAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })} - {new Date(log.createdAt).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                </div>

                {/* CORPO DA CONVERSA */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-4 pt-1">
                  <div className="md:col-span-5 bg-slate-900/60 p-3.5 rounded-xl border border-slate-800/60 space-y-1">
                    <span className="text-[10px] font-extrabold text-slate-500 uppercase tracking-wider block">👤 Mensagem do Visitante:</span>
                    <p className="text-xs text-slate-200 font-medium leading-relaxed">"{log.userMessage}"</p>
                  </div>
                  <div className="md:col-span-7 bg-indigo-950/20 p-3.5 rounded-xl border border-indigo-500/20 space-y-1">
                    <span className="text-[10px] font-extrabold text-indigo-400 uppercase tracking-wider block">🐝 Resposta do Concierge AI:</span>
                    <p className="text-xs text-slate-300 font-normal leading-relaxed whitespace-pre-wrap">{log.botReply}</p>
                    {log.recommendedUrl && (
                      <div className="pt-2">
                        <a
                          href={log.recommendedUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] font-extrabold text-emerald-400 hover:text-emerald-300 underline"
                        >
                          ↗ Link da Oferta Recomendada no Chat
                        </a>
                      </div>
                    )}
                  </div>
                </div>

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
