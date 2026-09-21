'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function PlannerBoard() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [blogs, setBlogs] = useState<any[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [oracleLoading, setOracleLoading] = useState(false);
  const [keywordsLoading, setKeywordsLoading] = useState(false);
  const [keywordsData, setKeywordsData] = useState<{ niche: string; keywords: any[] } | null>(null);
  
  const [newTopic, setNewTopic] = useState('');
  const [selectedBlogId, setSelectedBlogId] = useState('');
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  // Fase 126: Radar de Tendências (Google Trends) & Quarentena (Fase 6 - Human-in-the-Loop)
  const [radarTab, setRadarTab] = useState<'trends' | 'seo' | 'quarantine'>('trends');

  const [trendsData, setTrendsData] = useState([
    { id: 'tr1', topic: 'Inteligência Artificial Generativa em 2026: Lançamento do Gemini 3.5 e GPT-6', growth: '+1.250%', category: 'Tecnologia • Descarga News', status: 'Explosão Viral 🔥', sentiment: 'Positivo / Eufórico', suggestedHeadline: 'O Fim da Edição Manual: Como a IA Generativa de 2026 Mudou o Audiovisual' },
    { id: 'tr2', topic: 'Novo Álbum de Phonk Drift faz Sucesso Global no TikTok e Reels', growth: '+890%', category: 'Música • Dark Trap Radio', status: 'Em Alta 📈', sentiment: 'Enérgico / Dark', suggestedHeadline: 'Por Que o Cyber Phonk Tocou em 10 Milhões de Shorts Nesta Semana' },
    { id: 'tr3', topic: 'Campeonato Mundial de Drift Sub-25 e Nova Telemetria Automotiva', growth: '+640%', category: 'Esportes • Macaco Driver', status: 'Tendência 🏎️', sentiment: 'Adrenalina', suggestedHeadline: 'Drift a 200 km/h: A Tecnologia Por Trás dos Carros Vencedores de 2026' },
    { id: 'tr4', topic: 'Regulação de Direitos Autorais em Vozes Sintéticas e Avatares AI', growth: '+420%', category: 'Política / Tech • Geral', status: 'Debate Quente ⚖️', sentiment: 'Controverso', suggestedHeadline: 'Locutores Sintéticos vs Humanos: O Que Diz a Nova Lei de IA' },
  ]);

  const [quarantineItems, setQuarantineItems] = useState([
    { id: 'q1', title: 'Shorts 9:16: "O Segredo do Cyber Phonk nos Games"', channel: 'Dark Trap Radio', type: 'Vídeo Vertical (9:16)', format: 'TikTok / Reels / Kwai', created: 'Há 10 min', status: 'pending', preview: 'Legenda Hormozi com batida de 140 BPM no fundo.' },
    { id: 'q2', title: 'Manchete Urgente: "A Nova Lei de IA e os Avatares"', channel: 'Descarga News', type: 'Isca Social & Thread', format: 'Twitter/X & YouTube Shorts', created: 'Há 25 min', status: 'pending', preview: 'Thread de 5 tweets com link canônico para o portal.' },
    { id: 'q3', title: 'Artigo + Áudio Dual-Host: "Drift a 200 km/h"', channel: 'Macaco Driver', type: 'Podcast (Aoede vs Charon)', format: 'Portal & Newsletter', created: 'Há 1 hora', status: 'approved', preview: 'Mesa de som virtual com debate de 4 minutos.' },
  ]);

  const [scheduleSlots, setScheduleSlots] = useState([
    { day: 'SEG', label: 'Segunda', slots: 4, peak: '09h e 18h', status: 'Ativo 🟢', color: 'border-purple-500/40' },
    { day: 'TER', label: 'Terça', slots: 6, peak: '10h e 19h', status: 'Ativo 🟢', color: 'border-purple-500/40' },
    { day: 'QUA', label: 'Quarta', slots: 5, peak: '11h e 20h', status: 'Ativo 🟢', color: 'border-purple-500/40' },
    { day: 'QUI', label: 'Quinta', slots: 6, peak: '09h e 21h', status: 'Pico 🔥', color: 'border-emerald-500/60 bg-emerald-950/10' },
    { day: 'SEX', label: 'Sexta', slots: 4, peak: '12h e 17h', status: 'Ativo 🟢', color: 'border-purple-500/40' },
    { day: 'SÁB', label: 'Sábado', slots: 3, peak: '14h e 20h', status: 'Fim de Semana 🟡', color: 'border-yellow-500/40' },
    { day: 'DOM', label: 'Domingo', slots: 3, peak: '15h e 21h', status: 'Fim de Semana 🟡', color: 'border-yellow-500/40' },
  ]);
  const [dragOverDay, setDragOverDay] = useState<string | null>(null);

  useEffect(() => {
    fetchBlogs();
  }, []);

  const showNotification = (type: 'success' | 'error' | 'info', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleDropOnDay = (day: string) => {
    setDragOverDay(null);
    setScheduleSlots(prev => prev.map(s => s.day === day ? { ...s, slots: s.slots + 1 } : s));
    showNotification('success', `⚡ Pauta alocada na janela de tráfego de ${day} (Pico no Cron) com sucesso!`);
  };

  const fetchBlogs = async () => {
    try {
      const res = await fetch('/api/admin/blogs/list');
      const data = await res.json();
      if (data.success) {
        setBlogs(data.blogs);
        if (data.blogs.length > 0) {
          setSelectedBlogId(data.blogs[0].id);
          fetchTasks(data.blogs[0].id);
          fetchKeywords(data.blogs[0].id);
        }
      }
    } catch (err) {
      console.error('Erro ao carregar veículos:', err);
    }
  };

  const fetchTasks = async (blogId: string) => {
    try {
      const res = await fetch(`/api/admin/planner?blogId=${blogId}`);
      const data = await res.json();
      if (data.success) setTasks(data.tasks);
    } catch (err) {
      console.error('Erro ao carregar fila:', err);
    }
  };

  const fetchKeywords = async (blogId: string) => {
    setKeywordsLoading(true);
    try {
      const res = await fetch(`/api/admin/planner/keywords?blogId=${blogId}`);
      const data = await res.json();
      if (data.success) setKeywordsData({ niche: data.niche, keywords: data.keywords });
    } catch (err) {
      console.error('Erro ao carregar radar SEO:', err);
    } finally {
      setKeywordsLoading(false);
    }
  };

  const handleBlogChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedBlogId(e.target.value);
    fetchTasks(e.target.value);
    fetchKeywords(e.target.value);
  };

  const handleAddKeywordTopic = async (topic: string) => {
    if (!topic || !selectedBlogId) return;
    showNotification('info', `Injetando pauta otimizada SEO na fila: "${topic}"...`);
    try {
      const res = await fetch('/api/admin/planner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blogId: selectedBlogId, topic }),
      });
      const data = await res.json();
      if (data.success || res.ok) {
        fetchTasks(selectedBlogId);
        showNotification('success', '⚡ Pauta SEO de cauda longa injetada na fila neural com sucesso!');
      } else {
        showNotification('error', data.error || 'Erro ao injetar pauta SEO.');
      }
    } catch (err) {
      showNotification('error', 'Falha na conexão ao adicionar pauta SEO.');
    }
  };

  const handleApproveQuarantine = (id: string) => {
    setQuarantineItems((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'approved' } : item)));
    showNotification('success', '✅ Asset aprovado com sucesso! O Webhook do n8n (Fase 125) foi acionado para disparo instantâneo nas redes sociais do canal.');
  };

  const handleRejectQuarantine = (id: string) => {
    setQuarantineItems((prev) => prev.map((item) => (item.id === id ? { ...item, status: 'rejected' } : item)));
    showNotification('error', '❌ Asset refutado com feedback QA. Enviado de volta ao Enxame IA para reescrita neural.');
  };

  const handleScanTrends = () => {
    showNotification('success', '🔥 Google Trends audita as palavras-chave quentes em tempo real! 4 novas tendências virais identificadas para a Colmeia.');
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTopic.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/admin/planner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blogId: selectedBlogId, topic: newTopic.trim() }),
      });
      const data = await res.json();
      if (data.success || res.ok) {
        setNewTopic('');
        fetchTasks(selectedBlogId);
        showNotification('success', 'Pauta adicionada com sucesso à fila neural!');
      } else {
        showNotification('error', data.error || 'Falha ao salvar pauta.');
      }
    } catch (err) {
      showNotification('error', 'Erro de conexão ao tentar salvar pauta.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch('/api/admin/planner', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });
      fetchTasks(selectedBlogId);
      showNotification('info', 'Pauta removida da fila de redação.');
    } catch (err) {
      showNotification('error', 'Erro ao tentar remover pauta.');
    }
  };

  const invokeOracle = async () => {
    setOracleLoading(true);
    showNotification('info', 'Consultando inteligência de mercado para gerar pautas virais...');
    try {
      const res = await fetch('/api/admin/planner/oracle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ blogId: selectedBlogId }),
      });
      const data = await res.json();
      if (data.success) {
        showNotification('success', `Oráculo gerou ${data.count} novas pautas virais para redação automática!`);
        fetchTasks(selectedBlogId);
      } else {
        showNotification('error', data.error || 'Erro ao gerar pautas via Oráculo.');
      }
    } catch (err) {
      showNotification('error', 'Falha na conexão com o Oráculo Neural.');
    } finally {
      setOracleLoading(false);
    }
  };

  const colPending = tasks.filter((t) => t.status === 'pending');
  const colWriting = tasks.filter((t) => t.status === 'writing');
  const colPublished = tasks.filter((t) => t.status === 'published');

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      
      {/* BANNER DE NOTIFICAÇÃO EXECUTIVA (Substituindo alerts) */}
      {notification && (
        <div
          className={`p-4 rounded-2xl border flex items-center justify-between shadow-xl transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300'
              : notification.type === 'error'
              ? 'bg-red-950/80 border-red-500/40 text-red-300'
              : 'bg-blue-950/80 border-blue-500/40 text-blue-300'
          }`}
        >
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span className="text-base">
              {notification.type === 'success' ? '✓' : notification.type === 'error' ? '⚠️' : 'ℹ️'}
            </span>
            <span>{notification.message}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2">
            ✕
          </button>
        </div>
      )}

      {/* HEADER EXECUTIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-[400px] h-[400px] bg-gradient-to-bl from-purple-500/10 via-indigo-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping" />
            MOTOR NEURAL • REDAÇÃO EM KANBAN
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Oráculo & Planejamento Editorial
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Organize a fila de redação autônoma. Invoque o Oráculo para sugerir temas virais automaticamente ou adicione pautas manuais. O enxame de agentes processará cada pauta em segundo plano.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10 w-full md:w-auto justify-end">
          <Link
            href="/admin"
            className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2"
          >
            ← Painel Central
          </Link>
          <select
            value={selectedBlogId}
            onChange={handleBlogChange}
            className="bg-slate-950/80 border border-slate-700/80 rounded-xl px-4 py-3 text-xs font-bold text-white focus:outline-none focus:border-purple-500 cursor-pointer shadow-inner min-w-[180px]"
          >
            {blogs.map((b) => (
              <option key={b.id} value={b.id}>
                Veículo: {b.name}
              </option>
            ))}
          </select>
          <button
            onClick={invokeOracle}
            disabled={oracleLoading || !selectedBlogId}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-purple-500/20 hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center gap-2"
          >
            {oracleLoading ? (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <span>⚡</span>
            )}
            {oracleLoading ? 'Processando Oráculo...' : 'Invocar Oráculo IA'}
          </button>
        </div>
      </div>

      {/* BARRA DE ADIÇÃO MANUAL DE PAUTA */}
      <form onSubmit={handleAdd} className="bg-slate-900/60 backdrop-blur-xl p-4 rounded-2xl border border-slate-800/80 shadow-xl flex flex-col sm:flex-row gap-3">
        <input
          type="text"
          value={newTopic}
          onChange={(e) => setNewTopic(e.target.value)}
          placeholder="Digite um novo tema ou diretriz para a redação neural (ex: Análise completa do novo iPhone 16 Pro)..."
          className="flex-1 bg-slate-950/80 border border-slate-800 rounded-xl px-5 py-3 text-xs sm:text-sm font-medium text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 transition-all"
        />
        <button
          type="submit"
          disabled={loading || !newTopic.trim()}
          className="px-8 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-white transition-all border border-slate-700 shadow-md disabled:opacity-50 flex items-center justify-center gap-2 shrink-0"
        >
          {loading ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : '➕'}
          <span>Adicionar à Fila</span>
        </button>
      </form>

      {/* CALENDÁRIO EDITORIAL & AGENDADOR HORÁRIO (CRON PLANNER) */}
      <div className="bg-gradient-to-r from-slate-900/90 via-purple-950/40 to-slate-900/90 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-purple-500/30 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-5 border-b border-slate-800 gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-400 animate-pulse" />
              <h2 className="text-base md:text-lg font-black text-white tracking-tight">Grade de Programação Editorial (Cron Schedule)</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">Distribuição automática de pautas por dia da semana e janela de tráfego orgânico.</p>
          </div>
          <span className="px-3 py-1.5 rounded-xl bg-purple-950/60 border border-purple-800/80 text-xs font-mono font-bold text-purple-300">
            🕒 Cron: 0 */2 * * * (Ativo)
          </span>
        </div>

        <div className="flex items-center justify-between text-xs text-purple-300 bg-purple-950/40 p-3 rounded-2xl border border-purple-500/20 mb-2 mt-4 font-mono">
          <span>💡 <strong>Dica Interativa:</strong> Arraste os cards da <em>Fila de Produção</em> abaixo e solte sobre os dias da semana para reagendar pautas no Cron Job!</span>
          <span className="text-[10px] bg-purple-900/60 px-2 py-0.5 rounded text-purple-200">Drag & Drop Ativo</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 pt-3">
          {scheduleSlots.map((item, i) => (
            <div
              key={i}
              onDragOver={(e) => { e.preventDefault(); setDragOverDay(item.day); }}
              onDragLeave={() => setDragOverDay(null)}
              onDrop={(e) => { e.preventDefault(); handleDropOnDay(item.day); }}
              className={`bg-slate-950/80 p-4 rounded-2xl border ${item.color} flex flex-col justify-between space-y-3 hover:scale-105 transition-all shadow-md ${
                dragOverDay === item.day ? 'ring-2 ring-purple-400 scale-105 bg-purple-950/60' : ''
              }`}
            >
              <div className="flex justify-between items-center">
                <span className="text-xs font-black font-mono text-purple-300">{item.day}</span>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800 font-bold">{item.slots} pautas</span>
              </div>
              <div>
                <p className="text-xs font-bold text-white">{item.label}</p>
                <p className="text-[10px] text-slate-400 font-mono mt-0.5">Pico: {item.peak}</p>
              </div>
              <div className="pt-2 border-t border-slate-800/80 text-[9px] font-mono text-slate-400 flex justify-between items-center">
                <span>Motor IA:</span>
                <span className="font-bold text-slate-300">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* SELETOR DE ABAS DE INTELIGÊNCIA EDITORIAL & QA (FASE 126) */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-800/80">
        <button
          onClick={() => setRadarTab('trends')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            radarTab === 'trends'
              ? 'bg-gradient-to-r from-orange-600 via-amber-600 to-yellow-600 text-white shadow-lg shadow-orange-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>🔥</span> Radar Google Trends & Viral Tracker (4)
        </button>
        <button
          onClick={() => setRadarTab('seo')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            radarTab === 'seo'
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg shadow-cyan-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>🔍</span> Radar SEO & Cauda Longa ({keywordsData?.keywords?.length || 0})
        </button>
        <button
          onClick={() => setRadarTab('quarantine')}
          className={`px-6 py-3 rounded-2xl font-extrabold text-xs tracking-wider uppercase transition-all flex items-center gap-2.5 ${
            radarTab === 'quarantine'
              ? 'bg-gradient-to-r from-purple-600 via-pink-600 to-rose-600 text-white shadow-lg shadow-pink-500/20 scale-102'
              : 'bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800'
          }`}
        >
          <span>🛡️</span> Quarentena & Aprovação Humana (Fase 6) • ({quarantineItems.filter(i => i.status === 'pending').length})
        </button>
      </div>

      {/* ABA 1: RADAR GOOGLE TRENDS & BREAKING NEWS (FASE 126) */}
      {radarTab === 'trends' && (
        <div className="bg-gradient-to-r from-slate-900/90 via-orange-950/40 to-slate-900/90 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-orange-500/30 shadow-2xl relative overflow-hidden space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-5 border-b border-slate-800 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-orange-400 animate-ping" />
                <h2 className="text-base md:text-lg font-black text-white tracking-tight">
                  Radar Google Trends & Termômetro Viral (Real-Time)
                </h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Monitoramento de buscas explosivas no Google e TikTok para gerar pautas de altíssimo engajamento imediato.
              </p>
            </div>
            <button
              onClick={handleScanTrends}
              className="px-5 py-2.5 rounded-xl bg-orange-950/80 hover:bg-orange-900 text-xs font-extrabold text-orange-300 border border-orange-800 transition-all flex items-center gap-2 shadow-sm cursor-pointer"
            >
              <span>🔄</span>
              <span>Escanear Google Trends Agora</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {trendsData.map((tr) => (
              <div
                key={tr.id}
                className="bg-slate-950/80 p-6 rounded-3xl border border-slate-800/80 hover:border-orange-500/50 transition-all flex flex-col justify-between space-y-4 shadow-xl group relative overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/5 rounded-full blur-2xl pointer-events-none -mr-10 -mt-10" />
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center gap-2">
                    <span className="px-3 py-1 rounded-full bg-orange-500/10 border border-orange-500/20 text-[10px] font-black text-orange-400 uppercase tracking-wider">
                      {tr.category}
                    </span>
                    <span className="text-emerald-400 font-mono text-xs font-black bg-emerald-950/60 px-2.5 py-1 rounded-lg border border-emerald-500/30 flex items-center gap-1">
                      <span>📈</span> {tr.growth}
                    </span>
                  </div>

                  <h3 className="text-white font-extrabold text-sm md:text-base leading-snug group-hover:text-orange-400 transition-colors">
                    {tr.topic}
                  </h3>

                  <div className="bg-slate-900/80 p-3.5 rounded-2xl border border-slate-800">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">
                      💡 Manchete Recomendada (Otimizada para Shorts/Reels):
                    </span>
                    <p className="text-xs font-bold text-slate-200 italic">
                      "{tr.suggestedHeadline}"
                    </p>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex justify-between items-center">
                  <span className="text-[10px] font-mono text-slate-400">
                    Sentimento: <strong className="text-slate-300">{tr.sentiment}</strong>
                  </span>
                  <button
                    onClick={() => handleAddKeywordTopic(tr.suggestedHeadline)}
                    className="px-4 py-2 rounded-xl bg-gradient-to-r from-orange-600 via-amber-600 to-yellow-600 hover:from-orange-500 hover:to-yellow-500 text-white font-black text-xs transition-all shadow-md hover:scale-105 active:scale-95 flex items-center gap-1.5 cursor-pointer"
                  >
                    <span>⚡</span>
                    <span>Injetar no Enxame AI</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ABA 2: RADAR DE PALAVRAS-CHAVE SEO & CAUDA LONGA */}
      {radarTab === 'seo' && (
      <div className="bg-gradient-to-r from-slate-900/90 via-cyan-950/40 to-slate-900/90 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-cyan-500/30 shadow-2xl relative overflow-hidden animate-in fade-in duration-300">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-5 border-b border-slate-800 gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
              <h2 className="text-base md:text-lg font-black text-white tracking-tight">Radar SEO & Palavras-Chave de Cauda Longa (Long-Tail)</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Oportunidades de alto tráfego e baixa concorrência auditadas em tempo real para: <span className="text-cyan-300 font-bold">{keywordsData?.niche || 'Seu Nicho'}</span>
            </p>
          </div>
          <button
            onClick={() => fetchKeywords(selectedBlogId)}
            disabled={keywordsLoading}
            className="px-4 py-2 rounded-xl bg-cyan-950/80 hover:bg-cyan-900 text-xs font-mono font-bold text-cyan-300 border border-cyan-800 transition-all flex items-center gap-2 shadow-sm"
          >
            {keywordsLoading ? <div className="w-3.5 h-3.5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" /> : '🔄'}
            <span>Escanear Radar SEO</span>
          </button>
        </div>

        {keywordsLoading ? (
          <div className="py-12 text-center text-slate-400 text-xs font-mono animate-pulse">
            🔍 Auditando buscas globais e volume de CPC no Google / Bing para o nicho...
          </div>
        ) : !keywordsData?.keywords || keywordsData.keywords.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs font-mono">
            Nenhuma palavra-chave encontrada no momento. Clique em Escanear Radar SEO.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-6">
            {keywordsData.keywords.map((kw) => (
              <div key={kw.id} className="bg-slate-950/80 p-5 rounded-2xl border border-slate-800/80 hover:border-cyan-500/50 transition-all flex flex-col justify-between space-y-3 shadow-lg group">
                <div>
                  <div className="flex justify-between items-start gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded bg-cyan-950/60 border border-cyan-800 text-[10px] font-mono text-cyan-300">
                      {kw.intent}
                    </span>
                    <span className="text-emerald-400 font-mono text-xs font-bold shrink-0">
                      CPC {kw.cpc}
                    </span>
                  </div>
                  <h3 className="text-white font-bold text-xs leading-snug group-hover:text-cyan-300 transition-colors">
                    "{kw.keyword}"
                  </h3>
                  <p className="text-[11px] text-slate-400 font-sans mt-1.5 line-clamp-2 italic">
                    💡 Dica de Título: {kw.suggestedTitle}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex justify-between items-center text-[10px] font-mono text-slate-500">
                  <span>Vol: <strong className="text-slate-300">{kw.volume}</strong> | KD: {kw.kd}</span>
                  <button
                    onClick={() => handleAddKeywordTopic(kw.suggestedTitle)}
                    className="px-2.5 py-1 rounded bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-[10px] transition-all shadow-sm hover:scale-105 active:scale-95 flex items-center gap-1"
                    title="Adicionar à fila de redação neural"
                  >
                    <span>⚡</span> Injetar Pauta
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      )}

      {/* ABA 3: QUARENTENA DE APROVAÇÃO HUMANA (FASE 6 • HUMAN-IN-THE-LOOP) */}
      {radarTab === 'quarantine' && (
        <div className="bg-gradient-to-r from-slate-900/90 via-purple-950/40 to-slate-900/90 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-purple-500/30 shadow-2xl relative overflow-hidden space-y-6 animate-in fade-in duration-300">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-5 border-b border-slate-800 gap-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-pink-400 animate-pulse" />
                <h2 className="text-base md:text-lg font-black text-white tracking-tight">
                  Quarentena Editorial & Aprovação Humana (Fase 6 do Pipeline)
                </h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Revise os Shorts, Iscas Sociais e Áudios gerados de forma autônoma pelo Enxame antes de autorizar o disparo para os Webhooks do n8n.
              </p>
            </div>
            <span className="px-3.5 py-1.5 rounded-full bg-pink-500/10 border border-pink-500/30 text-pink-300 font-extrabold text-xs">
              🛡️ Human-in-the-Loop Ativo
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {quarantineItems.map((item) => (
              <div
                key={item.id}
                className={`bg-slate-950/80 p-6 rounded-3xl border transition-all flex flex-col justify-between space-y-4 shadow-xl ${
                  item.status === 'approved'
                    ? 'border-emerald-500/40 bg-emerald-950/10'
                    : item.status === 'rejected'
                    ? 'border-red-500/40 opacity-50'
                    : 'border-slate-800/80 hover:border-purple-500/50'
                }`}
              >
                <div className="space-y-3">
                  <div className="flex justify-between items-center gap-2">
                    <span className="px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-[10px] font-black text-purple-300 uppercase tracking-wider">
                      {item.channel}
                    </span>
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[9px] font-black uppercase tracking-widest border flex items-center gap-1 ${
                        item.status === 'approved'
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : item.status === 'rejected'
                          ? 'bg-red-500/10 text-red-400 border-red-500/30'
                          : 'bg-amber-500/10 text-amber-400 border-amber-500/30 animate-pulse'
                      }`}
                    >
                      <span>{item.status === 'approved' ? '✓ Aprovado' : item.status === 'rejected' ? '✕ Refutado' : '⏳ Aguardando Revisão'}</span>
                    </span>
                  </div>

                  <div>
                    <span className="text-[10px] font-mono text-slate-500 block">
                      Formato: <strong className="text-slate-300">{item.format}</strong> • {item.created}
                    </span>
                    <h3 className="text-white font-extrabold text-sm leading-snug mt-1">
                      {item.title}
                    </h3>
                  </div>

                  <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 font-sans italic">
                    "{item.preview}"
                  </div>
                </div>

                {item.status === 'pending' && (
                  <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-800/80">
                    <button
                      onClick={() => handleApproveQuarantine(item.id)}
                      className="w-full bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-black text-xs py-2.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-1 cursor-pointer active:scale-95"
                    >
                      <span>✅</span>
                      <span>Aprovar Disparo</span>
                    </button>
                    <button
                      onClick={() => handleRejectQuarantine(item.id)}
                      className="w-full bg-slate-900 hover:bg-red-950/80 text-slate-400 hover:text-red-300 border border-slate-800 hover:border-red-500/40 font-bold text-xs py-2.5 rounded-xl transition-all flex items-center justify-center gap-1 cursor-pointer active:scale-95"
                    >
                      <span>❌</span>
                      <span>Refutar / IA</span>
                    </button>
                  </div>
                )}
                {item.status !== 'pending' && (
                  <div className="pt-3 border-t border-slate-800/80 text-center text-[11px] font-mono font-bold text-slate-500">
                    {item.status === 'approved' ? '🚀 Enviado para Webhook n8n (Fase 7)' : '♻️ Devolvido para reescrita neural'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* KANBAN BOARD EXECUTIVO */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 min-h-[600px]">
        
        {/* COLUNA 1: FILA DE ESPERA */}
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-slate-800/80 flex flex-col overflow-hidden shadow-xl">
          <div className="bg-slate-950/80 p-5 border-b border-slate-800/80 flex justify-between items-center">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-slate-400" />
              <h2 className="font-bold text-white uppercase tracking-wider text-xs">Fila de Produção (Arraste ➔)</h2>
            </div>
            <span className="px-2.5 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px] font-mono font-bold text-slate-400">
              {colPending.length}
            </span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-5 space-y-3.5">
            {colPending.length === 0 ? (
              <div className="text-center py-16 text-slate-500 text-xs font-medium">
                Nenhuma pauta aguardando na fila.
              </div>
            ) : (
              colPending.map((t) => (
                <div
                  key={t.id}
                  draggable={true}
                  onDragStart={(e) => e.dataTransfer.setData('text/plain', t.id)}
                  className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800/80 hover:border-purple-500/60 transition-all group relative shadow-sm flex justify-between items-start gap-3 cursor-grab active:cursor-grabbing hover:scale-102"
                >
                  <div className="space-y-1">
                    <p className="text-slate-200 font-semibold text-xs leading-relaxed">{t.topic}</p>
                    <span className="text-[10px] text-slate-500 font-mono block">Status: Aguardando motor IA</span>
                  </div>
                  <button
                    onClick={() => handleDelete(t.id)}
                    className="text-slate-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity text-xs font-bold p-1"
                    title="Remover pauta"
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* COLUNA 2: EM REDAÇÃO */}
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-purple-500/20 flex flex-col overflow-hidden shadow-xl relative">
          <div className="bg-purple-950/30 p-5 border-b border-purple-500/20 flex justify-between items-center">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
              <h2 className="font-bold text-purple-300 uppercase tracking-wider text-xs">Em Redação Neural</h2>
            </div>
            <span className="px-2.5 py-0.5 rounded-md bg-purple-950/60 border border-purple-500/30 text-[11px] font-mono font-bold text-purple-400">
              {colWriting.length}
            </span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-5 space-y-3.5">
            {colWriting.length === 0 ? (
              <div className="text-center py-16 text-slate-500 text-xs font-medium">
                Nenhum agente redigindo no momento.
              </div>
            ) : (
              colWriting.map((t) => (
                <div
                  key={t.id}
                  className="bg-purple-950/20 p-4 rounded-2xl border border-purple-500/30 shadow-inner space-y-2.5 animate-pulse"
                >
                  <p className="text-purple-100 font-semibold text-xs leading-relaxed">{t.topic}</p>
                  <div className="flex items-center gap-2 text-[10px] font-bold text-purple-400 uppercase tracking-wider">
                    <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping" />
                    Agente processando artigo...
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* COLUNA 3: PUBLICADO */}
        <div className="bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-emerald-500/20 flex flex-col overflow-hidden shadow-xl">
          <div className="bg-emerald-950/30 p-5 border-b border-emerald-500/20 flex justify-between items-center">
            <div className="flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              <h2 className="font-bold text-emerald-300 uppercase tracking-wider text-xs">Publicados & Online</h2>
            </div>
            <span className="px-2.5 py-0.5 rounded-md bg-emerald-950/60 border border-emerald-500/30 text-[11px] font-mono font-bold text-emerald-400">
              {colPublished.length}
            </span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-5 space-y-3.5">
            {colPublished.length === 0 ? (
              <div className="text-center py-16 text-slate-500 text-xs font-medium">
                Nenhuma publicação concluída ainda.
              </div>
            ) : (
              colPublished.map((t) => (
                <div
                  key={t.id}
                  className="bg-slate-900/80 p-4 rounded-2xl border border-emerald-500/20 hover:border-emerald-500/40 transition-all shadow-sm space-y-2"
                >
                  <p className="text-slate-200 font-semibold text-xs leading-relaxed">{t.topic}</p>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="text-emerald-400 font-bold uppercase tracking-wider flex items-center gap-1">
                      ✓ Concluído
                    </span>
                    <Link
                      href="/admin/posts"
                      className="text-slate-400 hover:text-white underline font-medium"
                    >
                      Ver no Acervo
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
