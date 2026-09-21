'use client';

import React, { useState, useEffect, useRef } from 'react';

interface LogEntry {
  id: string;
  timestamp: string;
  module: string;
  severity: string;
  message: string;
}

export default function ObservabilityTerminal() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLive, setIsLive] = useState(true);
  const terminalRef = useRef<HTMLDivElement>(null);
  
  // Fake metrics
  const [cpuUsage, setCpuUsage] = useState(45);
  const [ramUsage, setRamUsage] = useState(62);

  useEffect(() => {
    // Initial fetch
    fetchLogs(null);

    // Polling interval for new logs
    const interval = setInterval(() => {
      if (isLive) {
        fetchLogs('latest');
        // Jiggle metrics
        setCpuUsage(prev => Math.max(10, Math.min(100, prev + (Math.random() * 20 - 10))));
        setRamUsage(prev => Math.max(20, Math.min(95, prev + (Math.random() * 10 - 5))));
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isLive]);

  const fetchLogs = async (lastId: string | null) => {
    try {
      const url = lastId ? `/api/admin/logs?lastId=${lastId}` : '/api/admin/logs';
      const res = await fetch(url);
      const data = await res.json();
      if (data.success && data.logs.length > 0) {
        setLogs(prev => {
          const newLogs = [...prev, ...data.logs];
          // Keep only last 500 logs to prevent memory leak in browser
          if (newLogs.length > 500) return newLogs.slice(newLogs.length - 500);
          return newLogs;
        });
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    // Auto-scroll to bottom
    if (terminalRef.current && isLive) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs, isLive]);

  const getSeverityColor = (sev: string) => {
    switch(sev) {
      case 'ERROR': return 'text-red-500';
      case 'WARN': return 'text-yellow-400';
      case 'DEBUG': return 'text-purple-400';
      case 'INFO':
      default: return 'text-emerald-400';
    }
  };

  const getModuleColor = (mod: string) => {
    switch(mod) {
      case 'SWARM': return 'text-cyan-400';
      case 'DAEMON': return 'text-blue-400';
      case 'PUBLISHER': return 'text-fuchsia-400';
      case 'PAYWALL': return 'text-amber-400';
      default: return 'text-slate-400';
    }
  };

  return (
    <div className="max-w-[1440px] mx-auto h-[calc(100vh-120px)] flex flex-col font-mono bg-[#050505] rounded-3xl border border-slate-800 shadow-2xl overflow-hidden animate-in fade-in duration-500 relative">
      
      {/* HEADER MATRIX STYLE */}
      <div className="bg-[#0a0a0a] border-b border-slate-800 p-4 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className={`w-3 h-3 rounded-full ${isLive ? 'bg-emerald-500 animate-pulse' : 'bg-slate-600'}`} />
            <span className="text-emerald-500 font-bold tracking-widest text-sm uppercase">Apollo OS - Live Telemetry</span>
          </div>
          
          <div className="h-6 w-px bg-slate-800 mx-2" />
          
          {/* Fake Metrics */}
          <div className="flex items-center gap-6 text-xs font-bold text-slate-500">
             <div className="flex items-center gap-2">
               <span>CPU LOAD</span>
               <div className="w-24 h-2 bg-slate-900 rounded-full overflow-hidden">
                 <div className={`h-full transition-all duration-500 ${cpuUsage > 85 ? 'bg-red-500' : 'bg-cyan-500'}`} style={{ width: `${cpuUsage}%` }} />
               </div>
               <span className="w-8 text-right">{Math.round(cpuUsage)}%</span>
             </div>
             
             <div className="flex items-center gap-2">
               <span>RAM</span>
               <div className="w-24 h-2 bg-slate-900 rounded-full overflow-hidden">
                 <div className={`h-full transition-all duration-500 ${ramUsage > 90 ? 'bg-red-500' : 'bg-purple-500'}`} style={{ width: `${ramUsage}%` }} />
               </div>
               <span className="w-8 text-right">{Math.round(ramUsage)}%</span>
             </div>
          </div>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={() => setIsLive(!isLive)}
            className={`px-4 py-1.5 rounded text-xs font-bold uppercase transition-colors border ${isLive ? 'border-red-500/50 text-red-500 hover:bg-red-500/10' : 'border-emerald-500/50 text-emerald-500 hover:bg-emerald-500/10'}`}
          >
            {isLive ? '■ Pause Stream' : '▶ Resume Stream'}
          </button>
          <button onClick={() => setLogs([])} className="px-4 py-1.5 rounded text-xs font-bold uppercase transition-colors border border-slate-700 text-slate-400 hover:bg-slate-800">
            Clear
          </button>
        </div>
      </div>

      {/* CONSOLE WINDOW */}
      <div 
        ref={terminalRef}
        className="flex-1 p-6 overflow-y-auto"
        style={{ scrollBehavior: 'smooth' }}
      >
        <div className="space-y-1.5">
          <div className="text-slate-500 text-xs mb-4">
            Welcome to Apollo OS Terminal. Neural swarm active. Awaiting logs...<br/>
            ----------------------------------------------------------------------
          </div>
          
          {logs.map((log) => (
            <div key={log.id} className="text-[13px] leading-relaxed flex items-start gap-3 hover:bg-white/5 p-1 -mx-1 rounded transition-colors group">
              <span className="text-slate-600 shrink-0 select-none">
                {new Date(log.timestamp).toISOString().split('T')[1].replace('Z', '')}
              </span>
              
              <span className={`shrink-0 w-16 font-bold ${getSeverityColor(log.severity)}`}>
                [{log.severity}]
              </span>
              
              <span className={`shrink-0 w-24 font-bold ${getModuleColor(log.module)}`}>
                {log.module}
              </span>
              
              <span className="text-emerald-50/80 break-words group-hover:text-emerald-400 transition-colors">
                {log.message}
              </span>
            </div>
          ))}
          
          {!isLive && (
             <div className="text-yellow-500 text-xs mt-4 animate-pulse">
               Stream paused. Scroll locked.
             </div>
          )}
        </div>
      </div>
      
      {/* FOOTER GLOW */}
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-emerald-500 to-transparent opacity-50 blur-[2px]" />
    </div>
  );
}
