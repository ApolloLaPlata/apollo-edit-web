import React from 'react';
import AdminNavigation from '@/components/admin/AdminNavigation';
import CommandPalette from '@/components/admin/CommandPalette';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex h-screen bg-slate-950 font-sans text-slate-300 overflow-hidden">
      
      {/* SIDEBAR & NAV RESPONSIVA (CLIENT COMPONENT) */}
      <AdminNavigation />
      <CommandPalette />

      {/* Área de Conteúdo Principal */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden bg-slate-900 relative">
        {/* HEADER DESKTOP (Escondido no mobile pois o AdminNavigation renderiza o dele) */}
        <header className="hidden md:flex h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur justify-between items-center px-8 z-10 shrink-0">
            <h2 className="text-xl font-bold text-slate-200">Painel de Controle</h2>
            <div className="flex items-center gap-6">
                
                {/* DICA COMMAND PALETTE */}
                <div className="flex items-center gap-2 bg-slate-800/50 border border-slate-700/50 px-3 py-1.5 rounded-lg text-xs text-slate-400 font-medium">
                  <span className="text-cyan-500">🔍</span> Buscar
                  <div className="flex gap-1 ml-2 font-mono font-bold">
                    <span className="bg-slate-700 text-slate-300 px-1.5 rounded border border-slate-600">Ctrl</span>
                    <span className="bg-slate-700 text-slate-300 px-1.5 rounded border border-slate-600">K</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 text-green-400 px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    Sistema Online
                </div>
            </div>
        </header>

        <div className="flex-1 overflow-y-auto p-4 md:p-8 mt-16 md:mt-0">
            {children}
        </div>
      </main>
    </div>
  );
}
