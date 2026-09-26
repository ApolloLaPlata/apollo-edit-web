import React from 'react';

export default function MaestroLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 selection:bg-red-500/30">
      <div className="flex">
        {/* Sidebar Minimalista */}
        <aside className="w-64 border-r border-slate-800/60 bg-slate-900/50 min-h-screen p-6 hidden md:block">
          <div className="flex items-center gap-3 mb-10">
            <div className="w-8 h-8 bg-red-600 rounded-lg flex items-center justify-center font-black text-white shadow-[0_0_15px_rgba(220,38,38,0.5)]">V3</div>
            <h1 className="font-black text-xl tracking-tight text-white">MAESTRO</h1>
          </div>
          <nav className="space-y-4 text-sm font-bold tracking-wide">
            <a href="#" className="flex items-center gap-3 text-red-500 opacity-100 transition"><span className="text-xl">⚡</span> Painel Nuclear</a>
            <a href="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition"><span className="text-xl">📝</span> Central IA</a>
            <a href="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition"><span className="text-xl">👑</span> Gamificação</a>
            <a href="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition"><span className="text-xl">💰</span> Paywalls & Bidding</a>
            <a href="#" className="flex items-center gap-3 text-slate-500 hover:text-slate-300 transition"><span className="text-xl">🛡️</span> Defesa & Logs</a>
          </nav>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 overflow-x-hidden">
          {children}
        </main>
      </div>
    </div>
  );
}
