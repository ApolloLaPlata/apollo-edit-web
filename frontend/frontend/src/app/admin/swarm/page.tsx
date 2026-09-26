'use client';

import React, { useState, useEffect } from 'react';

/**
 * 🌌 PAINEL DO ENXAME (Swarm Dashboard V6)
 * Permite ao Diretor assistir a I.A conversando consigo mesma (Auto-Correção).
 */
export default function SwarmDashboard() {
  const [logs, setLogs] = useState<{agent: string, message: string, color: string}[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const simulateSwarm = async () => {
    setIsRunning(true);
    setLogs([]);
    
    setLogs([{ agent: "SISTEMA", color: "text-blue-500", message: "🚀 Acordando o robô de Python (Watcher/Writer)... Aguarde o processamento." }]);

    try {
      const res = await fetch('/api/admin/swarm', { method: 'POST' });
      const data = await res.json();
      
      if (data.success) {
        const lines = data.log.split('\n').filter((l: string) => l.trim() !== '');
        lines.forEach((line: string, index: number) => {
          setTimeout(() => {
            setLogs(prev => [...prev, { agent: "ROBÔ", color: "text-green-400", message: line }]);
          }, index * 200);
        });
        
        setTimeout(() => {
          setLogs(prev => [...prev, { agent: "SISTEMA", color: "text-purple-400", message: "✅ Ciclo finalizado e publicado no Banco de Dados!" }]);
          setIsRunning(false);
        }, lines.length * 200 + 500);
      } else {
        setLogs(prev => [...prev, { agent: "ERRO", color: "text-red-500", message: `❌ Falha: ${data.error}` }]);
        setIsRunning(false);
      }
    } catch (e: any) {
      setLogs(prev => [...prev, { agent: "ERRO", color: "text-red-500", message: `❌ Falha de Rede: ${e.message}` }]);
      setIsRunning(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto min-h-screen bg-slate-950">
      
      <header className="mb-10 flex justify-between items-end border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-4xl font-black text-white flex items-center gap-3">
            <span className="text-5xl">🌌</span> Swarm Central
          </h1>
          <p className="text-slate-400 mt-2 font-medium">Observe a Redação Neural operando em tempo real.</p>
        </div>

        <button 
          onClick={simulateSwarm}
          disabled={isRunning}
          className={`px-8 py-4 rounded-lg font-black uppercase tracking-widest transition-all ${isRunning ? 'bg-slate-800 text-slate-600' : 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.5)]'}`}
        >
          {isRunning ? 'Enxame Operando...' : 'Despertar Redação I.A'}
        </button>
      </header>

      {/* Terminal Hacker View */}
      <div className="bg-[#0a0a0c] border border-slate-800 rounded-xl h-[600px] overflow-hidden flex flex-col font-mono shadow-2xl relative">
        
        {/* Topbar do Terminal */}
        <div className="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="text-slate-500 text-xs ml-4">root@omniverse-v6:~# ./swarm_engine</span>
        </div>

        {/* Logs */}
        <div className="p-6 flex-1 overflow-y-auto space-y-4">
          {logs.length === 0 && !isRunning && (
            <div className="text-slate-600 text-center mt-20">A Redação está dormindo. Desperte o Enxame.</div>
          )}

          {logs.map((log, i) => (
            <div key={i} className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <span className="text-slate-500 text-xs mr-4">[{new Date().toLocaleTimeString()}]</span>
              <span className={`font-bold ${log.color} uppercase w-32 inline-block`}>[{log.agent}]</span>
              <span className="text-slate-300 ml-2">{log.message}</span>
            </div>
          ))}

          {isRunning && (
            <div className="flex items-center gap-2 mt-4 text-slate-500">
              <span className="w-2 h-4 bg-slate-500 animate-pulse"></span> Aguardando rede neural...
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
