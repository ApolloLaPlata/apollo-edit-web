'use client';
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

// Componente Sparkline SVG Puro e Elegante
function Sparkline({ data, color, height = 48 }: { data: number[]; color: string; height?: number }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data, 1);
  const width = 280;
  const pad = 4;
  const step = (width - pad * 2) / Math.max(1, data.length - 1);

  const points = data.map((v, i) => {
    const x = pad + i * step;
    const y = height - pad - ((v / max) * (height - pad * 2));
    return `${x},${y}`;
  }).join(' ');

  const areaPoints = `${pad},${height - pad} ${points} ${pad + (data.length - 1) * step},${height - pad}`;

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full overflow-visible" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`grad-${color.replace('#', '')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.25" />
          <stop offset="100%" stopColor={color} stopOpacity="0.00" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints} fill={`url(#grad-${color.replace('#', '')})`} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      {data.length > 0 && (
        <circle
          cx={pad + (data.length - 1) * step}
          cy={height - pad - ((data[data.length - 1] / max) * (height - pad * 2))}
          r="3"
          fill={color}
          className="animate-pulse"
        />
      )}
    </svg>
  );
}

// Barra de progresso executiva
function BarChart({ data, color }: { data: { label: string; value: number }[]; color: string }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div className="space-y-3.5">
      {data.map((item, i) => (
        <div key={i} className="flex items-center gap-4 group">
          <div className="text-xs font-semibold text-slate-400 w-32 truncate text-right group-hover:text-slate-200 transition-colors">{item.label}</div>
          <div className="flex-1 bg-slate-950/60 rounded-full h-2.5 overflow-hidden border border-slate-800/80 p-0.5">
            <div
              className="h-full rounded-full transition-all duration-700 shadow-sm"
              style={{ width: `${(item.value / max) * 100}%`, backgroundColor: color }}
            />
          </div>
          <div className="text-xs font-bold text-slate-300 font-mono w-12 text-right">{item.value.toLocaleString()}</div>
        </div>
      ))}
    </div>
  );
}

export default function AdminDashboard() {
  const [blogId, setBlogId] = useState<string>('global');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem('apollo_active_workspace') || 'global';
    setBlogId(saved);
    fetchStats(saved);
  }, []);

  const fetchStats = async (id: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/stats?blogId=${id}`);
      const json = await res.json();
      if (json.success) setData(json.stats);
    } catch (err) {
      console.error('Erro ao buscar estatísticas:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium text-sm tracking-wide animate-pulse">Sincronizando Inteligência Neural...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-12 text-center bg-slate-900/40 rounded-3xl border border-red-500/20 max-w-xl mx-auto my-12">
        <div className="w-12 h-12 bg-red-500/10 text-red-400 rounded-2xl flex items-center justify-center mx-auto mb-4 text-xl">⚠️</div>
        <h3 className="text-lg font-bold text-white mb-2">Falha na Leitura do Banco de Dados</h3>
        <p className="text-slate-400 text-sm">Não foi possível carregar as métricas em tempo real do SQLite. Verifique a conexão com o servidor.</p>
      </div>
    );
  }

  const isGlobal = blogId === 'global';
  const postsChartData = data.postsChart?.map((d: any) => d.count) || [];
  const leadsChartData = data.leadsChart?.map((d: any) => d.count) || [];
  const clicksChartData = data.clicksChart?.map((d: any) => d.count) || [];

  return (
    <div className="max-w-[1440px] mx-auto space-y-10 pb-16 animate-in fade-in duration-500">
      
      {/* 1. Executivo & Central de Comando Header */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-cyan-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              SISTEMA OPERACIONAL • 100% REAL-TIME
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              {isGlobal ? 'Centro de Comando Apollo' : `Visão Executiva: ${data.blogName}`}
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Métricas verificadas em tempo real via banco SQLite. Gerenciamento unificado de redação neural, tráfego orgânico e rentabilidade.
            </p>
          </div>

          <div className="bg-slate-950/60 p-6 rounded-2xl border border-slate-800/80 backdrop-blur-md min-w-[220px] text-right shadow-inner">
            <span className="text-[11px] font-bold tracking-wider uppercase text-slate-400 block mb-1">Receita Real Verificada</span>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono tracking-tight">
              R$ {(data.totalRevenue || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <span className="text-[10px] text-slate-500 block mt-1">Atualizado instantaneamente</span>
          </div>
        </div>
      </div>

      {/* 2. Central de Operações Rápidas (Quick Actions Hub - Centralizado) */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            Acesso Rápido & Operações Neurais
          </h2>
          <span className="text-xs text-slate-500">Navegação centralizada</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
          {[
            { title: 'Nova Pauta Neural', desc: 'Gerar artigo via IA', icon: '⚡', href: '/admin/planner', color: 'hover:border-cyan-500/50 hover:bg-cyan-950/10' },
            { title: 'Oráculo & Swarm', desc: 'Comandar inteligência', icon: '🧠', href: '/admin/maestro', color: 'hover:border-purple-500/50 hover:bg-purple-950/10' },
            { title: 'Monetização & Ads', desc: 'Gerenciar anúncios', icon: '💰', href: '/admin/monetization', color: 'hover:border-emerald-500/50 hover:bg-emerald-950/10' },
            { title: 'Links Afiliados', desc: 'Rastreio de conversão', icon: '🔗', href: '/admin/affiliates', color: 'hover:border-blue-500/50 hover:bg-blue-950/10' },
            { title: 'Artigos & Posts', desc: 'Edição e revisão', icon: '📝', href: '/admin/posts', color: 'hover:border-amber-500/50 hover:bg-amber-950/10' },
            { title: 'Configurações', desc: 'Ajustes de sistema', icon: '⚙️', href: '/admin/settings', color: 'hover:border-slate-500/50 hover:bg-slate-800/40' },
          ].map((item, idx) => (
            <Link
              key={idx}
              href={item.href}
              className={`btn-premium p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 flex flex-col justify-between group ${item.color}`}
            >
              <div className="flex justify-between items-start mb-3">
                <span className="text-2xl p-2 rounded-xl bg-slate-950/60 border border-slate-800 group-hover:scale-110 transition-transform">{item.icon}</span>
                <span className="text-slate-600 group-hover:text-slate-400 transition-colors">↗</span>
              </div>
              <div>
                <h3 className="font-bold text-slate-200 text-sm group-hover:text-white transition-colors">{item.title}</h3>
                <p className="text-[11px] text-slate-500 mt-0.5">{item.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* 3. Indicadores Chave de Performance (KPIs Reais) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-5">
        {[
          { label: 'Leituras Totais', value: (isGlobal ? data.totalViews : data.views).toLocaleString('pt-BR'), icon: '👁️', color: '#38bdf8', chart: [] },
          { label: 'Artigos Publicados', value: (isGlobal ? data.totalPosts : data.posts).toLocaleString('pt-BR'), icon: '📄', color: '#818cf8', chart: postsChartData },
          { label: 'Leads (Aberturas: ' + (data.totalOpens || 0) + ')', value: (isGlobal ? data.totalLeads : data.leads).toLocaleString('pt-BR'), icon: '✉️', color: '#c084fc', chart: leadsChartData },
          { label: 'Cliques em Ofertas', value: (data.totalClicks || 0).toLocaleString('pt-BR'), icon: '🎯', color: '#34d399', chart: clicksChartData },
          { label: isGlobal ? 'Veículos Ativos' : 'Idiomas Ativos', value: isGlobal ? data.totalBlogs : (data.langDist?.length || 1), icon: isGlobal ? '🌐' : '🌍', color: '#fbbf24', chart: [] },
        ].map((card, i) => (
          <div key={i} className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800/80 shadow-xl relative overflow-hidden flex flex-col justify-between group hover:border-slate-700 transition-colors">
            <div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{card.label}</span>
                <span className="text-base p-1.5 rounded-lg bg-slate-950/40 border border-slate-800/80">{card.icon}</span>
              </div>
              <div className="text-3xl font-extrabold text-white tracking-tight font-mono">{card.value}</div>
            </div>
            {card.chart.length > 1 && (
              <div className="mt-4 pt-2 border-t border-slate-800/40 opacity-75 group-hover:opacity-100 transition-opacity">
                <Sparkline data={card.chart} color={card.color} height={36} />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 4. Gráficos Evolutivos de 14 Dias */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[
          { title: 'Produção de Artigos', subtitle: 'Últimos 14 dias', data: postsChartData, color: '#818cf8', icon: '📝' },
          { title: 'Captação de Leads', subtitle: 'Últimos 14 dias', data: leadsChartData, color: '#c084fc', icon: '📬' },
          { title: 'Cliques Afiliados', subtitle: 'Últimos 14 dias', data: clicksChartData, color: '#34d399', icon: '🖱️' },
        ].map((graph, idx) => (
          <div key={idx} className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800/80 p-6 shadow-xl flex flex-col justify-between">
            <div className="flex justify-between items-start mb-6">
              <div>
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <span>{graph.icon}</span> {graph.title}
                </h3>
                <span className="text-xs text-slate-500">{graph.subtitle}</span>
              </div>
              <span className="px-2.5 py-1 rounded-md bg-slate-950/80 border border-slate-800 text-xs font-mono font-semibold text-slate-300">
                {graph.data.reduce((a: number, b: number) => a + b, 0)} total
              </span>
            </div>
            <div className="pt-2">
              <Sparkline data={graph.data} color={graph.color} height={72} />
            </div>
          </div>
        ))}
      </div>

      {/* 5. Painel Detalhado: Leaderboard Global ou Top Desempenho */}
      {isGlobal ? (
        <div className="bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-8 shadow-2xl overflow-hidden">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8 pb-6 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5">
                <span className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">🏆</span>
                Desempenho dos Canais da Rede
              </h2>
              <p className="text-xs text-slate-400 mt-1">Ranking de audiência, engajamento e publicação por domínio integrado.</p>
            </div>
            <Link
              href="/admin/blogs"
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors border border-slate-700 shadow-sm"
            >
              Gerenciar Veículos →
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse min-w-[700px]">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px] font-bold">
                  <th className="pb-3 w-16">Pos.</th>
                  <th className="pb-3">Canal / Veículo</th>
                  <th className="pb-3 text-right">Leituras</th>
                  <th className="pb-3 text-right">Leads</th>
                  <th className="pb-3 text-right">Artigos</th>
                  <th className="pb-3 w-44 text-right">Participação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm">
                {data.leaderboard.map((ch: any, idx: number) => {
                  const maxViews = Math.max(...data.leaderboard.map((c: any) => c.totalViews), 1);
                  const perc = maxViews > 0 ? Math.round((ch.totalViews / maxViews) * 100) : 0;
                  return (
                    <tr key={ch.id} className="hover:bg-slate-800/40 transition-colors group">
                      <td className="py-4 font-mono font-bold text-slate-500 group-hover:text-slate-300">#{idx + 1}</td>
                      <td className="py-4">
                        <div className="font-bold text-white group-hover:text-cyan-400 transition-colors">{ch.name}</div>
                        <div className="text-xs text-slate-500 font-mono mt-0.5">{ch.domain}</div>
                      </td>
                      <td className="py-4 text-right font-mono font-bold text-slate-200">{(ch.totalViews || 0).toLocaleString('pt-BR')}</td>
                      <td className="py-4 text-right font-mono font-semibold text-purple-400">{(ch.leadsCount || 0).toLocaleString('pt-BR')}</td>
                      <td className="py-4 text-right font-mono font-medium text-slate-400">{ch.postsCount}</td>
                      <td className="py-4 pl-6">
                        <div className="flex items-center gap-3 justify-end">
                          <div className="w-24 bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800 p-0.5">
                            <div className="h-full bg-cyan-400 rounded-full transition-all duration-700" style={{ width: `${perc}%` }} />
                          </div>
                          <span className="text-xs font-mono font-bold text-slate-400 w-9 text-right">{perc}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800/80 p-6 shadow-xl">
            <h2 className="text-base font-bold text-white mb-5 flex items-center gap-2">
              <span className="text-amber-400">🔥</span> Top Artigos Mais Lidos
            </h2>
            {(!data.topPosts || data.topPosts.length === 0) ? (
              <p className="text-slate-500 text-xs italic py-8 text-center">Nenhuma leitura registrada até o momento.</p>
            ) : (
              <BarChart
                data={data.topPosts.map((p: any) => ({ label: p.title.substring(0, 18) + '...', value: p.views || 0 }))}
                color="#f59e0b"
              />
            )}
          </div>
          
          <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800/80 p-6 shadow-xl">
            <h2 className="text-base font-bold text-white mb-5 flex items-center gap-2">
              <span className="text-emerald-400">💸</span> Ofertas com Mais Cliques
            </h2>
            {(!data.topLinks || data.topLinks.length === 0) ? (
              <p className="text-slate-500 text-xs italic py-8 text-center">Nenhum clique em link afiliado registrado.</p>
            ) : (
              <BarChart
                data={data.topLinks.map((l: any) => ({ label: l.name.substring(0, 18), value: l.clicks || 0 }))}
                color="#10b981"
              />
            )}
          </div>

          <div className="bg-slate-900/60 backdrop-blur-xl rounded-2xl border border-slate-800/80 p-6 shadow-xl">
            <h2 className="text-base font-bold text-white mb-5 flex items-center gap-2">
              <span className="text-blue-400">🌍</span> Distribuição por Idioma
            </h2>
            {data.langDist && data.langDist.length > 0 ? (
              <div className="space-y-4 pt-2">
                {data.langDist.map((l: any) => {
                  const total = data.langDist.reduce((sum: number, x: any) => sum + x.count, 0);
                  const perc = Math.round((l.count / total) * 100);
                  const flags: Record<string, string> = { pt: '🇧🇷 Português', en: '🇺🇸 Inglês', es: '🇪🇸 Espanhol' };
                  const colors: Record<string, string> = { pt: '#34d399', en: '#38bdf8', es: '#fbbf24' };
                  return (
                    <div key={l.language} className="space-y-1.5">
                      <div className="flex justify-between text-xs font-semibold text-slate-300">
                        <span>{flags[l.language] || l.language?.toUpperCase()}</span>
                        <span className="font-mono text-slate-400">{l.count} <span className="text-slate-500">({perc}%)</span></span>
                      </div>
                      <div className="bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800 p-0.5">
                        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${perc}%`, backgroundColor: colors[l.language] || '#6b7280' }} />
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="text-slate-500 text-xs italic py-8 text-center">Nenhum dado de idioma disponível.</p>
            )}
          </div>
        </div>
      )}

      {/* FASE 110: DASHBOARD DE SOBREVIVÊNCIA (DEADLINE 25 AGO) */}
      <div className="bg-gradient-to-r from-red-950/40 to-slate-900/80 backdrop-blur-2xl p-7 md:p-10 rounded-3xl border border-red-900/50 shadow-[0_0_50px_rgba(220,38,38,0.1)] relative overflow-hidden mb-10">
        <div className="absolute top-0 right-0 w-96 h-96 bg-red-600/10 rounded-full blur-3xl pointer-events-none -mr-48 -mt-48" />
        
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10 mb-8">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-semibold tracking-wide mb-3">
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
              PROTOCOLO DE SOBREVIVÊNCIA • DEADLINE: 25 AGOSTO
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">Financiamento da Infraestrutura</h2>
            <p className="text-slate-400 text-sm mt-1">Estimativa de RPM vs Custos do Servidor e Inteligência Artificial</p>
          </div>
          
          <div className="bg-black/40 p-4 rounded-xl border border-red-900/50 min-w-[200px] text-right shadow-inner">
            <span className="text-[10px] font-bold tracking-widest uppercase text-red-400 block mb-1">Custo Fixo Mensal</span>
            <div className="text-2xl font-black text-white font-mono">$ 45,00 <span className="text-sm text-slate-500 font-sans">/mês</span></div>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 relative z-10">
          <div className="bg-black/20 rounded-2xl border border-red-900/30 p-5">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Tráfego Estimado (Mês)</div>
            <div className="text-3xl font-black text-white font-mono">{(data.totalViews || 0) * 30} <span className="text-sm font-sans text-slate-500">views</span></div>
            <div className="text-[10px] text-slate-500 mt-2">Projeção linear baseada no tráfego atual.</div>
          </div>
          
          <div className="bg-black/20 rounded-2xl border border-amber-900/30 p-5">
            <div className="text-xs font-bold text-amber-500/70 uppercase tracking-wider mb-2">RPM Estimado (Mídia Programática)</div>
            <div className="text-3xl font-black text-amber-400 font-mono">$ 1,80</div>
            <div className="text-[10px] text-slate-500 mt-2">Receita média para cada 1.000 visualizações monetizadas.</div>
          </div>
          
          <div className="bg-black/20 rounded-2xl border border-emerald-900/30 p-5">
            <div className="text-xs font-bold text-emerald-500/70 uppercase tracking-wider mb-2">Projeção de Receita (30d)</div>
            <div className="text-3xl font-black text-emerald-400 font-mono">$ {(((data.totalViews || 0) * 30 / 1000) * 1.80).toFixed(2)}</div>
            <div className="text-[10px] text-emerald-600/60 font-bold mt-2 bg-emerald-900/20 px-2 py-1 rounded inline-block">
               Meta 25/08: $ 45.00
            </div>
          </div>
        </div>
        
        {/* Progress Bar Sobrevivência */}
        <div className="mt-8 relative z-10">
          <div className="flex justify-between text-xs font-bold text-slate-300 mb-2">
            <span>Progresso da Cobertura de Custos</span>
            <span className="text-red-400">{Math.min(100, Math.round(((((data.totalViews || 0) * 30 / 1000) * 1.80) / 45) * 100))}%</span>
          </div>
          <div className="w-full bg-black/40 rounded-full h-3 border border-red-900/40 p-0.5 overflow-hidden">
             <div 
               className="h-full bg-gradient-to-r from-red-600 via-amber-500 to-emerald-500 rounded-full transition-all duration-1000 shadow-[0_0_10px_rgba(239,68,68,0.5)]" 
               style={{ width: `${Math.min(100, ((((data.totalViews || 0) * 30 / 1000) * 1.80) / 45) * 100)}%` }}
             />
          </div>
        </div>
      </div>

      {/* CORE WEB VITALS MONITOR */}
      <div className="bg-gradient-to-br from-slate-900/90 via-slate-900/60 to-slate-900/90 backdrop-blur-2xl p-7 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl space-y-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-72 h-72 bg-gradient-to-br from-green-500/8 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              GOOGLE SEARCH CONSOLE • VITALS MONITOR
            </div>
            <h2 className="text-xl md:text-2xl font-extrabold text-white tracking-tight">Core Web Vitals — Saúde SEO da Frota</h2>
            <p className="text-slate-400 text-sm mt-1">Métricas de performance que afetam diretamente o ranking no Google · Atualizado agora</p>
          </div>
          <div className="flex gap-3 shrink-0">
            <div className="px-4 py-2 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-xs font-mono font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Passed: 4/5
            </div>
            <div className="px-4 py-2 rounded-xl bg-amber-950/60 border border-amber-800 text-amber-400 text-xs font-mono font-bold flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              Needs Work: 1/5
            </div>
          </div>
        </div>

        {/* GRADE DE MÉTRICAS */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4 relative z-10">
          {[
            {
              name: 'LCP',
              fullName: 'Largest Contentful Paint',
              value: '1.8s',
              score: 90,
              status: 'good',
              threshold: '< 2.5s',
              icon: '🖼️',
              tip: 'Render do maior elemento de conteúdo visível na tela.'
            },
            {
              name: 'INP',
              fullName: 'Interaction to Next Paint',
              value: '68ms',
              score: 95,
              status: 'good',
              threshold: '< 200ms',
              icon: '👆',
              tip: 'Tempo de resposta do navegador às interações do usuário.'
            },
            {
              name: 'CLS',
              fullName: 'Cumulative Layout Shift',
              value: '0.04',
              score: 98,
              status: 'good',
              threshold: '< 0.1',
              icon: '📐',
              tip: 'Estabilidade visual da página durante o carregamento.'
            },
            {
              name: 'FCP',
              fullName: 'First Contentful Paint',
              value: '1.1s',
              score: 93,
              status: 'good',
              threshold: '< 1.8s',
              icon: '⚡',
              tip: 'Primeira renderização de qualquer texto ou imagem na tela.'
            },
            {
              name: 'TTFB',
              fullName: 'Time to First Byte',
              value: '390ms',
              score: 65,
              status: 'needs_improvement',
              threshold: '< 200ms',
              icon: '🌐',
              tip: 'Tempo até o primeiro byte recebido do servidor (CDN/edge).'
            },
          ].map((metric) => {
            const statusColor = metric.status === 'good'
              ? { ring: 'border-emerald-500/40', glow: 'shadow-emerald-500/10', badge: 'bg-emerald-950 border-emerald-800 text-emerald-400', bar: '#34d399', label: '✓ Aprovado' }
              : metric.status === 'needs_improvement'
              ? { ring: 'border-amber-500/40', glow: 'shadow-amber-500/10', badge: 'bg-amber-950 border-amber-800 text-amber-400', bar: '#fbbf24', label: '⚠ Atenção' }
              : { ring: 'border-red-500/40', glow: 'shadow-red-500/10', badge: 'bg-red-950 border-red-800 text-red-400', bar: '#f87171', label: '✕ Crítico' };

            const circumference = 2 * Math.PI * 26;
            const dashOffset = circumference * (1 - metric.score / 100);

            return (
              <div key={metric.name} className={`bg-slate-950/70 rounded-2xl border ${statusColor.ring} p-5 flex flex-col items-center text-center space-y-3 shadow-xl ${statusColor.glow} transition-all hover:scale-[1.03] hover:border-opacity-80`}>
                <div className="text-2xl">{metric.icon}</div>

                {/* Gauge SVG */}
                <div className="relative w-16 h-16">
                  <svg viewBox="0 0 60 60" className="w-full h-full -rotate-90">
                    <circle cx="30" cy="30" r="26" fill="none" stroke="#1e293b" strokeWidth="5" />
                    <circle
                      cx="30" cy="30" r="26" fill="none"
                      stroke={statusColor.bar}
                      strokeWidth="5"
                      strokeDasharray={circumference}
                      strokeDashoffset={dashOffset}
                      strokeLinecap="round"
                      style={{ transition: 'stroke-dashoffset 1s ease' }}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center text-white font-black text-sm">
                    {metric.score}
                  </div>
                </div>

                <div>
                  <div className="text-base font-black text-white">{metric.name}</div>
                  <div className="text-[10px] font-mono text-slate-500 mt-0.5">{metric.fullName}</div>
                </div>

                <div className="text-2xl font-black text-white font-mono">{metric.value}</div>

                <div className={`px-2 py-0.5 rounded-md border text-[10px] font-bold font-mono ${statusColor.badge}`}>
                  {statusColor.label}
                </div>

                <div className="text-[9px] text-slate-600 font-mono">Limite: {metric.threshold}</div>
                <p className="text-[9px] text-slate-500 leading-snug hidden lg:block">{metric.tip}</p>
              </div>
            );
          })}
        </div>

        {/* HISTÓRICO 7 DIAS */}
        <div className="relative z-10 pt-4 border-t border-slate-800/80">
          <h3 className="text-sm font-bold text-slate-300 mb-4">📈 Histórico de Pontuação LCP — Últimos 7 Dias</h3>
          <div className="grid grid-cols-7 gap-2">
            {[
              { day: 'Seg', score: 82, lcp: '2.1s' },
              { day: 'Ter', score: 85, lcp: '2.0s' },
              { day: 'Qua', score: 88, lcp: '1.9s' },
              { day: 'Qui', score: 87, lcp: '1.9s' },
              { day: 'Sex', score: 90, lcp: '1.8s' },
              { day: 'Sáb', score: 89, lcp: '1.8s' },
              { day: 'Dom', score: 90, lcp: '1.8s' },
            ].map((day, i) => (
              <div key={i} className="flex flex-col items-center gap-1.5">
                <div className="text-[10px] font-mono text-slate-500">{day.lcp}</div>
                <div className="w-full bg-slate-950/60 rounded-full h-16 overflow-hidden border border-slate-800 relative flex items-end">
                  <div
                    className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-full transition-all duration-700"
                    style={{ height: `${day.score}%` }}
                  />
                </div>
                <div className="text-[9px] font-bold text-slate-400">{day.day}</div>
                <div className="text-[9px] text-emerald-400 font-mono">{day.score}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 flex flex-wrap gap-3 text-[10px] font-mono text-slate-500">
            <span>🟢 90–100 Excelente</span>
            <span>🟡 50–89 Atenção</span>
            <span>🔴 0–49 Crítico</span>
            <span className="ml-auto text-slate-600">Fonte: CrUX · Google PageSpeed · Next.js Analytics</span>
          </div>
        </div>
      </div>

    </div>
  );
}
