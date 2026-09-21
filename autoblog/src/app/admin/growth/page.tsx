'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface BaitItem {
  id: string;
  blogId: string;
  platform: string;
  targetUrl: string;
  targetTitle: string;
  targetAuthor?: string;
  generatedComment: string;
  hookType: string;
  linkedArticleId?: string;
  linkedArticleSlug?: string;
  status: string;
  clicks: number;
  createdAt: string;
}

interface GrowthStats {
  totalGenerated: number;
  totalClicks: number;
  ctrEstimated: string;
  byPlatform: { platform: string; count: number; clicks: number }[];
  recentBaits: BaitItem[];
}

export default function GrowthDashboard() {
  const [stats, setStats] = useState<GrowthStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedBlog, setSelectedBlog] = useState('');
  const [testUrl, setTestUrl] = useState('https://youtube.com/watch?v=exemplo_viral');
  const [testTitle, setTestTitle] = useState('A Evolução da Inteligência Artificial em 2026 e o Futuro do Trabalho');
  const [generating, setGenerating] = useState(false);
  const [generatedBaits, setGeneratedBaits] = useState<any[]>([]);
  const [notification, setNotification] = useState<string | null>(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const url = selectedBlog ? `/api/admin/growth?blogId=${selectedBlog}` : '/api/admin/growth';
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Erro ao buscar estatísticas de growth:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [selectedBlog]);

  const handleGenerateTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    setGeneratedBaits([]);
    try {
      const res = await fetch('/api/admin/growth', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'generate_bait',
          blogId: selectedBlog || 'descarga-news',
          platform: testUrl.includes('twitter') || testUrl.includes('x.com') ? 'twitter' : 'youtube',
          targetUrl: testUrl,
          targetTitle: testTitle,
          targetAuthor: 'Canal Viral Em Alta'
        })
      });
      const data = await res.json();
      if (data.success) {
        setGeneratedBaits(data.baits || []);
        setNotification('⚡ 3 Iscas de alta conversão geradas com sucesso!');
        fetchStats(); // Atualizar estatísticas na hora
      } else {
        alert('Erro: ' + (data.error || 'Falha na geração'));
      }
    } catch (err: any) {
      alert('Erro de rede: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const getPlatformIcon = (plat: string) => {
    if (plat === 'youtube') return '📺';
    if (plat === 'twitter' || plat === 'x') return '🐦';
    if (plat === 'instagram') return '📸';
    if (plat === 'tiktok') return '🎵';
    return '🌐';
  };

  const getHookBadge = (type: string) => {
    if (type === 'CURATED_HOOK') return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-sky-950 text-sky-400 border border-sky-800">🪝 Gancho Magnético</span>;
    if (type === 'CONTROVERSIAL_DATA') return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-950 text-purple-400 border border-purple-800">⚡ Dado Técnico & Controvérsia</span>;
    return <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">💎 Resumo + Link Direct</span>;
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-16 font-sans animate-in fade-in duration-500">
      
      {/* HEADER DO PAINEL */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-96 h-96 rounded-full bg-emerald-500/10 blur-3xl pointer-events-none -mr-32 -mt-32" />
        <div className="space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            FASE 7 DO PIPELINE • GROWTH HACKING & TRÁFEGO ORGÂNICO
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Motor de Iscas Mercadológicas (Bait Injector)
          </h1>
          <p className="text-slate-400 text-sm max-w-2xl font-normal leading-relaxed">
            Gere comentários magnéticos com inteligência artificial para injetar em vídeos virais do YouTube, Twitter/X e TikTok, redirecionando milhares de visitantes altamente qualificados para os seus portais.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link href="/admin" className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2">
            ← Painel Central
          </Link>
          <a href="#test-generator" className="px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-xs font-extrabold text-black transition-all shadow-lg shadow-emerald-500/20 flex items-center gap-2">
            ⚡ Gerador de Isca Manual
          </a>
        </div>
      </div>

      {/* BANNER DA EXTENSÃO DO CHROME / EDGE */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 rounded-2xl border border-indigo-500/30 flex flex-col sm:flex-row items-center justify-between gap-6 shadow-xl">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-2xl shrink-0">
            🧩
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Extensão Oficial de Navegador (Chrome / Edge / Firefox)
              <span className="text-[10px] bg-indigo-500 text-white font-extrabold px-2 py-0.5 rounded-full">v2.5 PRONTA</span>
            </h3>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">
              Injete o botão <strong>"⚡ Gerar Isca Colmeia"</strong> diretamente na interface de comentários do YouTube e do X! A extensão já está compilada na pasta <code className="bg-slate-950 px-1.5 py-0.5 rounded text-indigo-400 font-mono">extensions/bait-injector</code>.
            </p>
          </div>
        </div>
        <div className="shrink-0 flex gap-3">
          <button onClick={() => alert('Como instalar:\n\n1. Abra o navegador em chrome://extensions\n2. Ative o "Modo do desenvolvedor" no canto superior direito\n3. Clique em "Carregar sem compactação"\n4. Selecione a pasta: E:\\MEUS PROGRAMAS\\AUTO_BLOG_CMS\\extensions\\bait-injector\n\nPronto! O botão mágico aparecerá nos comentários do YouTube!')} className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white shadow-md transition-all">
            📥 Como Instalar no Navegador
          </button>
        </div>
      </div>

      {/* TELEMETRIA & KPIS */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">🪝 Iscas Geradas (Total)</span>
          <div className="text-3xl font-black text-white">{loading ? '...' : stats?.totalGenerated || 0}</div>
          <span className="text-[11px] text-emerald-400 font-medium">↑ 100% autônomo & contextual</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">🎯 Cliques Rastreados</span>
          <div className="text-3xl font-black text-emerald-400">{loading ? '...' : stats?.totalClicks || 0}</div>
          <span className="text-[11px] text-slate-400 font-medium">Tráfego orgânico capturado</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">📈 Taxa de Conversão (CTR)</span>
          <div className="text-3xl font-black text-sky-400">{loading ? '...' : stats?.ctrEstimated || '0.0%'}</div>
          <span className="text-[11px] text-slate-400 font-medium">Média de cliques por comentário</span>
        </div>

        <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-2xl border border-slate-800 shadow-lg space-y-2">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">⚡ Redes Ativas</span>
          <div className="text-3xl font-black text-purple-400">{loading ? '...' : (stats?.byPlatform?.length || 4)}</div>
          <span className="text-[11px] text-slate-400 font-medium">YouTube, X/Twitter, IG & TikTok</span>
        </div>
      </div>

      {/* SELETOR DE PORTAL PARA FILTRO */}
      <div className="flex items-center justify-between bg-slate-900/40 p-4 rounded-2xl border border-slate-800">
        <span className="text-xs font-bold text-slate-300">Filtrar Telemetria por Portal da Rede:</span>
        <select
          value={selectedBlog}
          onChange={(e) => setSelectedBlog(e.target.value)}
          className="bg-slate-950 border border-slate-700 text-white text-xs font-bold px-4 py-2 rounded-xl outline-none focus:border-emerald-500"
        >
          <option value="">🌐 Todos os Portais da Frota</option>
          <option value="dark-trap">🎵 Dark Trap Radio (Phonk & Trap)</option>
          <option value="descarga-news">📰 Descarga News (Notícias & IA)</option>
          <option value="macaco-driver">🏎️ Macaco Driver (Automotivo)</option>
        </select>
      </div>

      {/* GERADOR DE ISCA MANUAL (SIMULADOR DO BACKEND) */}
      <div id="test-generator" className="bg-slate-900/80 backdrop-blur-2xl p-8 rounded-3xl border border-emerald-500/30 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <span>⚡ Laboratório de Iscas Mercadológicas</span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-2 py-0.5 rounded font-bold">SIMULADOR IA</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">Cole a URL e o título de um vídeo em alta no YouTube ou postagem no X para testar o motor neural.</p>
          </div>
        </div>

        <form onSubmit={handleGenerateTest} className="grid grid-cols-1 md:grid-cols-12 gap-4">
          <div className="md:col-span-4">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">URL da Postagem Alvo</label>
            <input
              type="text"
              value={testUrl}
              onChange={(e) => setTestUrl(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
              required
            />
          </div>
          <div className="md:col-span-5">
            <label className="block text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">Título / Manchete Alvo</label>
            <input
              type="text"
              value={testTitle}
              onChange={(e) => setTestTitle(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white font-semibold focus:outline-none focus:border-emerald-500"
              required
            />
          </div>
          <div className="md:col-span-3 flex items-end">
            <button
              type="submit"
              disabled={generating}
              className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-black font-extrabold text-xs py-3.5 px-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {generating ? '⏳ Gerando com IA...' : '⚡ Gerar 3 Iscas Agora'}
            </button>
          </div>
        </form>

        {/* RESULTADO GERADO */}
        {generatedBaits.length > 0 && (
          <div className="space-y-4 pt-4 border-t border-slate-800/80 animate-in fade-in duration-300">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block">✨ 3 Comentários Magnéticos Gerados com Sucesso:</span>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {generatedBaits.map((bait, idx) => (
                <div key={idx} className="bg-slate-950 p-5 rounded-2xl border border-slate-800 hover:border-emerald-500/50 transition-all space-y-3 flex flex-col justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white">{bait.label}</span>
                      {getHookBadge(bait.hookType)}
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed font-normal whitespace-pre-wrap bg-slate-900/60 p-3 rounded-xl border border-slate-800/60">
                      {bait.comment}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(bait.comment);
                      alert('✅ Comentário copiado para a área de transferência!');
                    }}
                    className="w-full py-2 rounded-xl bg-slate-900 hover:bg-emerald-500 hover:text-black text-xs font-bold text-slate-300 transition-colors border border-slate-800 flex items-center justify-center gap-1.5"
                  >
                    <span>📋 Copiar Isca para Postar</span>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* HISTÓRICO DE ISCAS GERADAS RECENTEMENTE */}
      <div className="bg-slate-900/60 backdrop-blur-xl p-8 rounded-3xl border border-slate-800 shadow-xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <span>🗂️ Histórico de Iscas & Link-Building</span>
            <span className="text-xs bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full font-mono">
              {stats?.recentBaits?.length || 0} registros
            </span>
          </h2>
          <button onClick={fetchStats} className="text-xs text-slate-400 hover:text-white font-bold flex items-center gap-1">
            <span>🔄</span> <span>Atualizar Dados</span>
          </button>
        </div>

        {loading ? (
          <div className="py-16 text-center text-slate-500 font-mono text-xs">Carregando telemetria...</div>
        ) : !stats?.recentBaits || stats.recentBaits.length === 0 ? (
          <div className="py-16 text-center text-slate-500 bg-slate-950/40 rounded-2xl border border-dashed border-slate-800 p-8">
            <span className="text-3xl block mb-2">🪝</span>
            <h3 className="font-bold text-sm text-slate-300">Nenhuma isca registrada até o momento</h3>
            <p className="text-xs text-slate-500 mt-1">Utilize o laboratório acima ou a extensão do navegador para disparar comentários magnéticos nas redes sociais.</p>
          </div>
        ) : (
          <div className="divide-y divide-slate-800/60">
            {stats.recentBaits.map((item) => (
              <div key={item.id} className="py-5 first:pt-0 last:pb-0 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 group">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-base" title={item.platform}>{getPlatformIcon(item.platform)}</span>
                    <span className="font-bold text-white truncate max-w-md">{item.targetTitle}</span>
                    <span className="text-slate-500 font-mono text-[10px]">({new Date(item.createdAt).toLocaleDateString('pt-BR')})</span>
                    {getHookBadge(item.hookType)}
                  </div>
                  <p className="text-xs text-slate-300 line-clamp-2 font-normal bg-slate-950/50 p-2.5 rounded-lg border border-slate-800/40">
                    "{item.generatedComment}"
                  </p>
                </div>

                <div className="shrink-0 flex items-center gap-4 text-right">
                  <div>
                    <div className="text-xs font-bold text-emerald-400">{item.clicks} cliques</div>
                    <div className="text-[10px] text-slate-500">em {item.linkedArticleSlug ? `/${item.linkedArticleSlug}` : 'home'}</div>
                  </div>
                  <a
                    href={item.targetUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white text-xs font-bold transition-colors"
                  >
                    ↗ Ver Alvo
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
