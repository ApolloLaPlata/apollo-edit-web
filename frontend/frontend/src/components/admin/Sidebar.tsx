'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import WorkspaceSwitcher from './WorkspaceSwitcher';

export default function Sidebar() {
  const pathname = usePathname();

  if (pathname === '/admin/kiosk') {
    return null;
  }

  const links = [
    {
      group: 'Visão Geral',
      items: [
        { href: '/admin', icon: '📊', label: 'Dashboard Executivo', exact: true },
        { href: '/admin/posts', icon: '📝', label: 'Artigos & Redação' },
        { href: '/admin/categories', icon: '🏷️', label: 'Categorias' },
        { href: '/admin/media', icon: '🖼️', label: 'Galeria de Mídia' },
        { href: '/admin/reports', icon: '📑', label: 'Auditoria & Relatórios', color: 'text-amber-400' },
      ],
    },
    {
      group: 'Design & Monetização',
      items: [
        { href: '/admin/appearance', icon: '🎨', label: 'Estúdio Visual (UI/UX)' },
        { href: '/admin/affiliates', icon: '💰', label: 'Automonetizador', color: 'text-yellow-400' },
        { href: '/admin/monetization', icon: '📈', label: 'Telemetria AdSense', color: 'text-emerald-400' },
        { href: '/admin/ads', icon: '📺', label: 'Inventário de Ads', color: 'text-cyan-400' },
      ],
    },
    {
      group: 'Audiência & Social',
      items: [
        { href: '/admin/concierge', icon: '💬', label: 'Concierge AI (Fase 8)', color: 'text-indigo-300' },
        { href: '/admin/growth', icon: '🪝', label: 'Isca Mercadológica (Fase 7)', color: 'text-indigo-400' },
        { href: '/admin/newsletter', icon: '✉️', label: 'Carteiro Neural', color: 'text-orange-400' },
        { href: '/admin/leads', icon: '📬', label: 'CRM & Base VIP', color: 'text-pink-400' },
        { href: '/admin/social', icon: '📣', label: 'Agente Social (Omni)', color: 'text-blue-400' },
        { href: '/admin/seo', icon: '⚡', label: 'Auditoria SEO & Web Vitals', color: 'text-emerald-400' },
      ],
    },
    {
      group: 'Inteligência Neural',
      items: [
        { href: '/admin/tasks', icon: '📋', label: 'Fila Kanban (IA)', color: 'text-amber-400' },
        { href: '/admin/planner', icon: '🔮', label: 'Oráculo de Pautas', color: 'text-purple-400' },
        { href: '/admin/maestro', icon: '🧠', label: 'Console Maestro', color: 'text-cyan-400' },
        { href: '/admin/syndicate', icon: '🌐', label: 'Sindicato Neural (Cross-Post)', color: 'text-cyan-300' },
        { href: '/admin/logs', icon: '💻', label: 'Terminal Holográfico (Logs)', color: 'text-emerald-500' },
        { href: '/admin/console', icon: '🖥️', label: 'Terminal Executivo', color: 'text-green-400' },
        { href: '/admin/settings', icon: '⚙️', label: 'Parâmetros & Webhooks' },
        { href: '/admin/blogs', icon: '🚀', label: 'Frota de Veículos', color: 'text-indigo-400' },
        { href: '/admin/plugins', icon: '🔌', label: 'Mercado de Plugins' },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-slate-900/80 backdrop-blur-2xl border-r border-slate-800/80 flex flex-col transition-all relative z-20 shadow-2xl">
      <div className="p-6 border-b border-slate-800/80 flex flex-col items-center text-center">
        <div className="w-14 h-14 bg-gradient-to-tr from-blue-600 to-cyan-500 text-white rounded-2xl flex items-center justify-center text-2xl mb-3 shadow-lg shadow-blue-500/20">
          ⚡
        </div>
        <h1 className="text-2xl font-black tracking-tight text-white">
          Auto<span className="text-blue-500">Blog</span> CMS
        </h1>
        <p className="text-[10px] text-cyan-400 mt-1 uppercase tracking-widest font-black">Colmeia Neural v2.0</p>
      </div>

      <nav className="flex-1 overflow-y-auto py-4 space-y-1 px-3 custom-scrollbar">
        <WorkspaceSwitcher />

        {links.map((group, i) => (
          <div key={i}>
            <p className="text-[10px] uppercase tracking-widest text-slate-500 font-extrabold mb-2 ml-3 mt-6">
              {group.group}
            </p>
            {group.items.map((item: any, j) => {
              const isActive = item.exact ? pathname === item.href : pathname.startsWith(item.href);
              const colorClass = item.color ? item.color : 'text-slate-300';
              const activeClass = isActive
                ? 'bg-slate-800/90 shadow-md border-slate-700 font-black text-white'
                : 'border-transparent hover:bg-slate-800/40 hover:border-slate-800 text-slate-400 hover:text-slate-200';

              return (
                <Link
                  key={j}
                  href={item.href}
                  className={`w-full text-left px-3.5 py-2.5 rounded-xl flex items-center gap-3 transition-all border mb-1 text-xs font-bold ${colorClass} ${activeClass}`}
                >
                  <span className="text-base">{item.icon}</span>
                  <span className={isActive ? 'text-white' : ''}>{item.label}</span>
                  {isActive && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 ml-auto animate-pulse" />}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
