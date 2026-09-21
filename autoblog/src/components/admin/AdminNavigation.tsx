'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import WorkspaceSwitcher from './WorkspaceSwitcher';

export default function AdminNavigation() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [health, setHealth] = useState({
    memoryPercent: 0,
    memoryLabel: '0MB',
    uptime: '0s',
    status: 'LOADING',
    dbStatus: 'ONLINE (<1ms)',
    totalPosts: 0,
    pendingQueue: 0,
    activeLeads: 0,
  });

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('/api/admin/health');
        const data = await res.json();
        if (data.success) setHealth(data.stats);
      } catch (e) {}
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  if (pathname === '/admin/kiosk') {
    return null;
  }

  const links = [
    { group: 'Visão Geral', items: [
      { href: '/admin', icon: '📊', label: 'Dashboard', exact: true },
      { href: '/admin/posts', icon: '📝', label: 'Todos os Posts' },
      { href: '/admin/tasks', icon: '📋', label: 'Quadro Kanban', color: 'text-indigo-400' },
      { href: '/admin/categories', icon: '🏷️', label: 'Categorias' },
      { href: '/admin/media', icon: '🖼️', label: 'Mídia (Imagens)' },
    ]},
    { group: 'Design e Receita', items: [
      { href: '/admin/appearance', icon: '🎨', label: 'Aparência' },
      { href: '/admin/affiliates', icon: '💰', label: 'Automonetizador', color: 'text-yellow-400' },
      { href: '/admin/monetization', icon: '📈', label: 'Relatório AdSense', color: 'text-emerald-400' },
      { href: '/admin/ads', icon: '📺', label: 'Ads Manager', color: 'text-cyan-400' },
    ]},
    { group: 'CRM e Redes Sociais', items: [
      { href: '/admin/concierge', icon: '💬', label: 'Concierge AI (Fase 8)', color: 'text-indigo-300' },
      { href: '/admin/growth', icon: '🪝', label: 'Isca Mercadológica (Fase 7)', color: 'text-indigo-400' },
      { href: '/admin/newsletter', icon: '✉️', label: 'CRM Neural', color: 'text-orange-400' },
      { href: '/admin/leads', icon: '📬', label: 'Base de Leads', color: 'text-pink-400' },
      { href: '/admin/social', icon: '📣', label: 'O Megafone (Social)', color: 'text-blue-400' },
    ]},
    { group: 'Infraestrutura IA', items: [
      { href: '/admin/sources', icon: '🕷️', label: 'Spider Web (Fontes RSS)', color: 'text-red-400' },
      { href: '/admin/knowledge-base', icon: '🌌', label: 'Cérebro Vetorial (RAG)', color: 'text-fuchsia-500' },
      { href: '/admin/autonomous', icon: '🧠', label: 'Cérebro Autônomo (Fase 132)', color: 'text-cyan-400' },
      { href: '/admin/synapses', icon: '🕸️', label: 'Sinapses & SEO (Fase 133)', color: 'text-purple-400' },
      { href: '/admin/immune', icon: '🛡️', label: 'Sistema Imune (Fase 134)', color: 'text-emerald-400' },
      { href: '/admin/genesis', icon: '🌟', label: 'Gênese & Nichos (Fase 135)', color: 'text-amber-400' },
      { href: '/admin/endocrine', icon: '⚗️', label: 'Sistema Endócrino (Fase 136)', color: 'text-sky-400' },
      { href: '/admin/crosschannel', icon: '📡', label: 'Telemetria Cross-Channel (Fase 137)', color: 'text-rose-400' },
      { href: '/admin/trend', icon: '🔮', label: 'Oráculo Preditor (Fase 138)', color: 'text-fuchsia-400' },
      { href: '/admin/seohealer', icon: '🛠️', label: 'Auto-Healer SEO (Fase 139)', color: 'text-teal-400' },
      { href: '/admin/console', icon: '🖥️', label: 'Terminal Hacker', color: 'text-green-400' },
      { href: '/admin/settings', icon: '⚙️', label: 'Cérebro do Canal' },
      { href: '/admin/blogs', icon: '🤖', label: 'Sala dos Diretores', color: 'text-indigo-400' },
      { href: '/admin/plugins', icon: '🔌', label: 'Mercado de Plugins' },
    ]},
  ];

  return (
    <>
      {/* HEADER MOBILE & DESKTOP (Topbar) */}
      <header className="absolute top-0 left-0 w-full h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur flex justify-between items-center px-4 md:px-8 z-30 shrink-0 md:hidden">
         <div className="flex items-center gap-3">
           <button 
             onClick={() => setIsOpen(true)}
             className="md:hidden text-slate-300 hover:text-white bg-slate-800 p-2 rounded-lg"
           >
             <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
           </button>
           <h2 className="text-xl font-bold text-slate-200">AutoBlog</h2>
         </div>
         <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/30 text-green-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
             <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
             <span className="hidden sm:inline">Online</span>
         </div>
      </header>

      {/* OVERLAY MOBILE */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden" 
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* SIDEBAR */}
      <aside className={`fixed md:relative top-0 left-0 h-screen w-72 md:w-64 bg-slate-900/95 md:bg-slate-900/60 backdrop-blur-2xl border-r border-slate-800/80 flex flex-col transition-transform duration-300 ease-in-out z-50 ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}>
        
        {/* CLOSE BUTTON MOBILE */}
        <button 
          onClick={() => setIsOpen(false)}
          className="absolute top-4 right-4 text-slate-400 hover:text-white md:hidden bg-slate-800 p-2 rounded-lg"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <div className="p-6 border-b border-slate-700/50 flex flex-col items-center text-center mt-8 md:mt-0">
          <div className="w-16 h-16 bg-blue-600/20 text-blue-500 rounded-2xl flex items-center justify-center text-3xl mb-3 shadow-[0_0_15px_rgba(59,130,246,0.3)]">
            🚀
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Auto<span className="text-blue-500">Blog</span> CMS</h1>
          <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-bold">Painel Executivo</p>
        </div>
        
        <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-3 custom-scrollbar">
          <WorkspaceSwitcher />

          {links.map((group, i) => (
            <div key={i}>
              <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2 ml-2 mt-6">{group.group}</p>
              {group.items.map((item, j) => {
                const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
                const colorClass = item.color ? item.color : 'text-slate-300';
                const activeClass = isActive ? 'bg-slate-800/90 shadow-inner border-slate-700 font-black text-white' : 'border-transparent hover:bg-slate-800/40 hover:border-slate-700/50';

                return (
                  <Link 
                    key={j} 
                    href={item.href} 
                    onClick={() => setIsOpen(false)}
                    className={`w-full text-left px-4 py-2.5 rounded-xl flex items-center gap-3 transition-all border mb-1 ${colorClass} ${activeClass}`}
                  >
                    <span className="text-lg">{item.icon}</span>
                    <span className={isActive ? 'text-white' : ''}>{item.label}</span>
                  </Link>
                )
              })}
            </div>
          ))}
        </nav>

        {/* SYSTEM STATUS WIDGET NO RODAPÉ */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-widest">Motor Principal</span>
            <div className="flex items-center gap-1.5">
              <span className={`w-1.5 h-1.5 rounded-full animate-pulse ${health.status === 'ONLINE' ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              <span className={`text-[10px] font-black ${health.status === 'ONLINE' ? 'text-emerald-400' : 'text-red-400'}`}>{health.status}</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="bg-slate-950 rounded-full h-1.5 overflow-hidden">
              <div className="h-full bg-blue-500 rounded-full transition-all duration-1000" style={{ width: `${health.memoryPercent}%` }}></div>
            </div>
            <div className="flex justify-between text-[9px] font-bold text-slate-500 font-mono">
              <span>RAM: {health.memoryLabel}</span>
              <span>PM2: {health.uptime}</span>
            </div>
            <div className="flex justify-between text-[9px] font-bold text-slate-400 font-mono pt-1 border-t border-slate-800/60">
              <span className="text-cyan-400">DB: {health.dbStatus || 'ONLINE'}</span>
              <span className="text-purple-400">Fila: {health.pendingQueue ?? 0} pautas</span>
            </div>
          </div>
        </div>

      </aside>
    </>
  );
}
