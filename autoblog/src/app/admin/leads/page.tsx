'use client';

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';

interface Lead {
  id: string;
  email: string;
  blogName: string;
  createdAt: string;
}

interface Campaign {
  id: string;
  subject: string;
  blogName: string;
  sentCount: number;
  contentHtml: string;
  createdAt: string;
}

export default function LeadsPage() {
  const [blogId, setBlogId] = useState<string>('global');
  const [data, setData] = useState<{ leads: Lead[]; campaigns: Campaign[] }>({ leads: [], campaigns: [] });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [notification, setNotification] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('apollo_active_workspace') || 'global';
    setBlogId(saved);
    fetchData(saved);
  }, []);

  const fetchData = async (id: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/leads?blogId=${id}`);
      const json = await res.json();
      if (json.success) {
        setData({ leads: json.leads || [], campaigns: json.campaigns || [] });
      }
    } catch (err) {
      console.error('Erro ao buscar dados do CRM:', err);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (msg: string) => {
    setNotification(msg);
    setTimeout(() => setNotification(null), 4000);
  };

  const handleExportCSV = () => {
    if (data.leads.length === 0) {
      showToast('⚠️ Nenhum lead na base para exportar.');
      return;
    }

    const headers = 'ID,Email,Portal,Data de Captura\n';
    const rows = data.leads
      .map((l) => `"${l.id}","${l.email}","${l.blogName || 'Geral'}","${new Date(l.createdAt).toLocaleDateString('pt-BR')}"`)
      .join('\n');
    const csvContent = 'data:text/csv;charset=utf-8,' + encodeURIComponent(headers + rows);

    const link = document.createElement('a');
    link.setAttribute('href', csvContent);
    link.setAttribute('download', `base_leads_vip_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast('✓ Arquivo CSV exportado e baixado com sucesso!');
  };

  const filteredLeads = useMemo(() => {
    return data.leads.filter(
      (l) =>
        l.email.toLowerCase().includes(search.toLowerCase()) ||
        (l.blogName && l.blogName.toLowerCase().includes(search.toLowerCase()))
    );
  }, [data.leads, search]);

  const totalSent = useMemo(() => {
    return data.campaigns.reduce((acc, c) => acc + (c.sentCount || 0), 0);
  }, [data.campaigns]);

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* BANNER DE NOTIFICAÇÃO EXECUTIVA */}
      {notification && (
        <div className="p-4 rounded-2xl bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 flex items-center justify-between shadow-xl animate-in slide-in-from-top-2 duration-300">
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span>✓</span>
            <span>{notification}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2">
            ✕
          </button>
        </div>
      )}

      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-emerald-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            CRM NEURAL • RETENÇÃO OMNI-CHANNEL
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Base de Leads & Histórico de Campanhas
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Monitore em tempo real os leitores VIP capturados por Exit-Intent na rede e analise o histórico do Carteiro Neural (disparos automatizados de newsletter).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link
            href="/admin"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Painel Central
          </Link>
          <Link
            href="/admin/newsletter"
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
          >
            <span>🚀</span> Estúdio do Carteiro Neural
          </Link>
        </div>
      </div>

      {/* KPI CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Leads VIP Capturados</span>
          <div className="text-3xl font-extrabold text-white font-mono">{loading ? '...' : data.leads.length}</div>
          <span className="text-[11px] text-emerald-400 font-semibold mt-1 block">✓ Base verificada no SQLite</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Campanhas Disparadas</span>
          <div className="text-3xl font-extrabold text-blue-400 font-mono">{loading ? '...' : data.campaigns.length}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">Edições redigidas pela IA</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg">
          <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Total de Envios</span>
          <div className="text-3xl font-extrabold text-emerald-400 font-mono">{loading ? '...' : totalSent}</div>
          <span className="text-[11px] text-slate-400 mt-1 block">E-mails entregues aos leitores</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-lg flex flex-col justify-between">
          <div>
            <span className="text-slate-500 text-[11px] font-bold uppercase tracking-wider block mb-1">Motor do Carteiro</span>
            <div className="text-lg font-bold text-slate-200 flex items-center gap-2 mt-1">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Automático (24h / CRON)
            </div>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">Disparo autônomo nas janelas da noite</span>
        </div>
      </div>

      {/* GRID PRINCIPAL: LEADS vs CAMPANHAS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* COLUNA DE LEADS VIP */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-6 md:p-8 shadow-xl flex flex-col h-[650px]">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                <span>👥</span> Lista de Assinantes VIP ({filteredLeads.length})
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">E-mails registrados via pop-up de retenção.</p>
            </div>
            
            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="text"
                placeholder="Filtrar e-mail..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="bg-slate-950/80 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 w-full sm:w-40 transition-all"
              />
              <button
                onClick={handleExportCSV}
                className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition-all shadow-sm shrink-0 flex items-center gap-1.5 active:scale-95"
                title="Baixar lista completa em formato CSV"
              >
                <span>📥</span> Exportar CSV
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 pr-2 no-scrollbar">
            {loading ? (
              <div className="py-20 text-center text-slate-500 text-xs font-semibold animate-pulse">Carregando base de dados do SQLite...</div>
            ) : filteredLeads.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-950/30">
                <span className="text-4xl mb-3 opacity-40">📭</span>
                <p className="font-bold text-sm text-slate-400">Nenhum assinante encontrado.</p>
                <p className="text-xs text-slate-600 mt-1">Os e-mails aparecerão aqui assim que forem capturados nos portais.</p>
              </div>
            ) : (
              filteredLeads.map((lead) => (
                <div
                  key={lead.id}
                  className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800/80 flex justify-between items-center hover:border-slate-700 transition-all group"
                >
                  <div className="min-w-0 pr-4">
                    <p className="text-slate-200 font-bold font-mono text-xs md:text-sm group-hover:text-emerald-400 transition-colors truncate">
                      {lead.email}
                    </p>
                    {lead.blogName && (
                      <span className="text-[10px] font-bold text-blue-400 uppercase tracking-wider bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/20 inline-block mt-1">
                        {lead.blogName}
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] font-mono font-semibold text-slate-500 bg-slate-900 px-2.5 py-1 rounded-lg border border-slate-800 shrink-0">
                    {new Date(lead.createdAt).toLocaleDateString('pt-BR')}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* COLUNA DE CAMPANHAS DO CARTEIRO */}
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-6 md:p-8 shadow-xl flex flex-col h-[650px]">
          <div className="flex justify-between items-center mb-6 pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
                <span>💌</span> Edições Enviadas pela IA ({data.campaigns.length})
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">Histórico do Carteiro Neural autônomo.</p>
            </div>
            <span className="text-[10px] uppercase font-bold text-blue-400 tracking-wider bg-blue-500/10 px-3 py-1 rounded-full border border-blue-500/20">
              Cron 24h Ativo
            </span>
          </div>

          <div className="flex-1 overflow-y-auto space-y-4 pr-2 no-scrollbar">
            {loading ? (
              <div className="py-20 text-center text-slate-500 text-xs font-semibold animate-pulse">Carregando campanhas enviadas...</div>
            ) : data.campaigns.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-slate-500 border border-dashed border-slate-800 rounded-2xl bg-slate-950/30 text-center px-6">
                <span className="text-4xl mb-3 opacity-40">🤖</span>
                <p className="font-bold text-sm text-slate-400">Nenhuma campanha enviada até o momento.</p>
                <p className="text-xs text-slate-600 mt-1 max-w-xs">
                  O Cérebro Neural agendará o disparo da newsletter assim que os novos artigos virais da semana acumularem leituras.
                </p>
              </div>
            ) : (
              data.campaigns.map((camp) => (
                <div
                  key={camp.id}
                  className="bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 hover:border-slate-700 transition-all flex flex-col justify-between space-y-3 group"
                >
                  <div className="flex justify-between items-start gap-4">
                    <h3 className="text-white font-bold text-sm group-hover:text-blue-400 transition-colors leading-snug">
                      {camp.subject}
                    </h3>
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 shrink-0">
                      Enviado
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-900">
                    <span className="flex items-center gap-1">
                      <span>👥</span>
                      <strong className="text-slate-300">{camp.sentCount}</strong> entregas
                    </span>
                    <span>{new Date(camp.createdAt).toLocaleDateString('pt-BR')}</span>
                    <button
                      onClick={() => setSelectedCampaign(camp)}
                      className="text-blue-400 hover:text-blue-300 font-sans font-bold underline transition-colors"
                    >
                      Ver Carta HTML ↗
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* MODAL DE PREVIEW DA CARTA HTML */}
      {selectedCampaign && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 md:p-8 max-w-3xl w-full shadow-2xl space-y-6 max-h-[85vh] flex flex-col relative">
            <div className="flex justify-between items-center border-b border-slate-800 pb-4 shrink-0">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 block mb-1">
                  Carta Redigida pela IA • {selectedCampaign.blogName || 'Geral'}
                </span>
                <h3 className="font-extrabold text-base md:text-lg text-white leading-snug">{selectedCampaign.subject}</h3>
              </div>
              <button
                onClick={() => setSelectedCampaign(null)}
                className="w-8 h-8 rounded-lg bg-slate-800 text-slate-400 hover:text-white flex items-center justify-center text-xs font-bold transition-colors shrink-0"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto bg-white rounded-2xl p-6 md:p-8 text-slate-900 font-serif prose prose-sm max-w-none shadow-inner border-4 border-slate-800">
              <div dangerouslySetInnerHTML={{ __html: selectedCampaign.contentHtml }} />
            </div>

            <div className="flex justify-between items-center pt-2 shrink-0">
              <span className="text-xs text-slate-500 font-mono">
                Entregue para {selectedCampaign.sentCount} leitores VIP em {new Date(selectedCampaign.createdAt).toLocaleString('pt-BR')}
              </span>
              <button
                onClick={() => setSelectedCampaign(null)}
                className="px-6 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white transition-colors"
              >
                Fechar Visualização
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
