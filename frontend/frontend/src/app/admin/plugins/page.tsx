import React from 'react';
import db from '@/lib/db';
import { toggleAgentConfig } from './actions';
import WatcherForm from './WatcherForm';

export const dynamic = 'force-dynamic';

export default async function PluginsPage() {
  const blogs = db
    .prepare(`
    SELECT Blog.id, Blog.name, Blog.domain, AgentConfig.isActive 
    FROM Blog 
    LEFT JOIN AgentConfig ON Blog.id = AgentConfig.blogId
  `)
    .all() as any[];

  return (
    <div className="max-w-[1440px] mx-auto space-y-10 pb-16 animate-in fade-in duration-500">
      {/* HEADER CORPORATIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-purple-500/10 via-pink-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
              MERCADO DE PLUGINS NEURAIS • IA OMNI
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Ecossistema de Plugins & Inteligência
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Ative ou configure módulos cognitivos avançados para o seu exército editorial. Gerencie a redação autônoma, síntese de áudio realista (TTS) e prospecção viral via YouTube Scraper em toda a frota.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Plugins Ativos</span>
              <span className="text-2xl font-extrabold text-white font-mono">3 / 3</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Motor Redator</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">Online</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Áudio Neural</span>
              <span className="text-2xl font-extrabold text-purple-400 font-mono">Ativo</span>
            </div>
          </div>
        </div>
      </div>

      {/* GRID DE PLUGINS ENTERPRISE */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        {/* PLUGIN 1: CORE AI ENGINE (ENXAME CRIADOR) */}
        <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-blue-500/30 p-8 shadow-2xl relative overflow-hidden group hover:border-blue-500/60 transition-all hover:shadow-[0_10px_30px_rgba(59,130,246,0.15)] flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-blue-500/20 transition-colors pointer-events-none" />

          <div>
            <div className="flex justify-between items-start mb-6">
              <div className="w-14 h-14 bg-blue-950/80 text-blue-400 rounded-2xl border border-blue-500/30 flex items-center justify-center text-3xl shadow-inner group-hover:scale-105 transition-transform">
                🧠
              </div>
              <span className="bg-blue-500/10 text-blue-400 font-black px-3 py-1 rounded-full text-[10px] uppercase tracking-widest border border-blue-500/20 shadow-sm">
                Módulo Base (Core)
              </span>
            </div>

            <h3 className="text-white font-extrabold text-xl">Enxame Criador</h3>
            <p className="text-xs text-blue-400 font-bold uppercase tracking-wider mt-1">
              Pesquisador & Redator Autônomo
            </p>
            <p className="text-sm text-slate-300 mt-4 leading-relaxed">
              Controla o motor principal de Inteligência Artificial que redige reportagens diárias. Desative para transformar um portal em redação 100% humana.
            </p>
          </div>

          <div className="space-y-3 mt-8 pt-6 border-t border-slate-800/80">
            <h4 className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-2">
              Status Operacional por Veículo
            </h4>
            {blogs.map((blog) => (
              <div
                key={blog.id}
                className="flex justify-between items-center bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80 hover:border-blue-500/30 transition-colors"
              >
                <div className="truncate pr-2">
                  <span className="text-xs font-bold text-slate-200 block truncate">{blog.name}</span>
                  <span className="text-[10px] font-mono text-slate-500 truncate">{blog.domain}</span>
                </div>
                <form action={toggleAgentConfig.bind(null, blog.id, !blog.isActive) as any}>
                  <button
                    type="submit"
                    className={`w-12 h-6 rounded-full relative transition-all shadow-inner border ${
                      blog.isActive
                        ? 'bg-blue-600 border-blue-500 shadow-blue-500/50'
                        : 'bg-slate-800 border-slate-700'
                    }`}
                  >
                    <div
                      className={`absolute top-0.5 left-0.5 bg-white w-4 h-4 rounded-full transition-transform shadow-md ${
                        blog.isActive ? 'translate-x-6' : ''
                      }`}
                    />
                  </button>
                </form>
              </div>
            ))}
          </div>
        </div>

        {/* PLUGIN 2: LEITOR NEURAL TTS (ATIVADO E INTEGRADO) */}
        <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-purple-500/30 p-8 shadow-2xl relative overflow-hidden group hover:border-purple-500/60 transition-all hover:shadow-[0_10px_30px_rgba(168,85,247,0.15)] flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-purple-500/20 transition-colors pointer-events-none" />

          <div>
            <div className="flex justify-between items-start mb-6">
              <div className="w-14 h-14 bg-purple-950/80 text-purple-400 rounded-2xl border border-purple-500/30 flex items-center justify-center text-3xl shadow-inner group-hover:scale-105 transition-transform">
                🎙️
              </div>
              <span className="bg-emerald-500/10 text-emerald-400 font-black px-3 py-1 rounded-full text-[10px] uppercase tracking-widest border border-emerald-500/20 shadow-sm flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                Online • Ativo
              </span>
            </div>

            <h3 className="text-white font-extrabold text-xl">Leitor Neural (TTS)</h3>
            <p className="text-xs text-purple-400 font-bold uppercase tracking-wider mt-1">
              Síntese de Voz & Smart Podcast
            </p>
            <p className="text-sm text-slate-300 mt-4 leading-relaxed">
              Gera automaticamente um player interativo de áudio neural para cada matéria publicada. Conectado ao endpoint <code className="text-purple-300 font-mono text-xs">/api/tts</code> com suporte a cache de voz.
            </p>
          </div>

          <div className="space-y-4 mt-8 pt-6 border-t border-slate-800/80">
            <div className="bg-purple-950/40 border border-purple-500/20 rounded-2xl p-4 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-extrabold uppercase tracking-widest text-purple-300">
                  Status de Síntese
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400">100% Funcional</span>
              </div>
              <p className="text-[11px] text-slate-400 leading-normal">
                O áudio é sintetizado em tempo real quando o leitor clica no player na página da matéria.
              </p>
            </div>

            <div className="flex items-center justify-between px-2 text-xs font-bold text-slate-400">
              <span>Cobertura na Frota</span>
              <span className="text-white font-mono">{blogs.length} / {blogs.length} Portais</span>
            </div>
          </div>
        </div>

        {/* PLUGIN 3: O WATCHER (YOUTUBE SCRAPER) */}
        <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-red-500/30 p-8 shadow-2xl relative overflow-hidden group hover:border-red-500/60 transition-all hover:shadow-[0_10px_30px_rgba(239,68,68,0.15)] flex flex-col justify-between">
          <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-red-500/20 transition-colors pointer-events-none" />

          <div>
            <div className="flex justify-between items-start mb-6">
              <div className="w-14 h-14 bg-red-950/80 text-red-400 rounded-2xl border border-red-500/30 flex items-center justify-center text-3xl shadow-inner group-hover:scale-105 transition-transform">
                👁️
              </div>
              <span className="bg-red-500/10 text-red-400 font-black px-3 py-1 rounded-full text-[10px] uppercase tracking-widest border border-red-500/20 shadow-sm animate-pulse">
                Radar Viral
              </span>
            </div>

            <h3 className="text-white font-extrabold text-xl">O Watcher (Spy)</h3>
            <p className="text-xs text-red-400 font-bold uppercase tracking-wider mt-1">
              Hacker de Vídeos & Comentários
            </p>
            <p className="text-sm text-slate-300 mt-4 leading-relaxed">
              Espiona canais e vídeos virais do YouTube em tempo real. Extrai as maiores dúvidas nos comentários e redige reportagens respondendo às dores reais da audiência.
            </p>
          </div>

          <div className="mt-8 pt-6 border-t border-slate-800/80">
            <WatcherForm blogs={blogs.map((b) => ({ id: b.id, name: b.name }))} />
          </div>
        </div>
      </div>
    </div>
  );
}
