'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

export default function ConsoleClient() {
  const [logs, setLogs] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Simula uma conexão SSE/WebSocket recebendo os logs do daemon e do PM2
    const interval = setInterval(() => {
      const msgs = [
        '[DAEMON] Verificando fila de publicações...',
        '[FFMPEG] Renderizando video_781293.mp4 na thread 2...',
        '[API] Rota /api/admin/blogs acessada pelo SuperAdmin.',
        '[SWARM] Agente do TechPulse terminou de gerar matéria.',
        '[TELEMETRY] Prometheus metric exportado.',
        '[MUTANT ENGINE] Bounce Rate: 42%. Nenhuma mutação.',
        '[SEO HEALER] Corrigindo tag H2 quebrada em Post #912.',
        '[MODAL ENGINE] Flux 2 Dev Upscale finalizado em 63s.',
      ];
      const randomMsg = msgs[Math.floor(Math.random() * msgs.length)];
      const timestamp = new Date().toISOString();
      setLogs(prev => [...prev.slice(-49), `[${timestamp}] ${randomMsg}`]);
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="max-w-[1440px] mx-auto space-y-6 pb-16 animate-in fade-in duration-500">
      <div className="flex justify-between items-center bg-slate-900/60 p-6 rounded-2xl border border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <span>💻</span> Console / Observabilidade (Fase 91)
          </h1>
          <p className="text-slate-400 text-sm">Acompanhe os batimentos cardíacos do sistema PM2 em tempo real.</p>
        </div>
        <Link href="/admin" className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm transition-colors border border-slate-700">
          Voltar
        </Link>
      </div>

      <div className="bg-[#0c0c0c] border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative">
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-xs font-mono text-slate-500 ml-2">root@apollo-cms:~</span>
        </div>
        
        <div ref={scrollRef} className="p-4 h-[600px] overflow-y-auto font-mono text-xs md:text-sm text-green-400 space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="opacity-90 hover:opacity-100 hover:bg-slate-800/30 px-1 py-0.5 rounded transition-colors">
              <span className="text-slate-500 mr-2">$</span>
              {log}
            </div>
          ))}
          {logs.length === 0 && <div className="text-slate-500 animate-pulse">Aguardando sinais vitais...</div>}
        </div>
      </div>
    </div>
  );
}
