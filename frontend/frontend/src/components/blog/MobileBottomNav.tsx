'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function MobileBottomNav({ domain }: { domain: string }) {
  const pathname = usePathname();
  
  // Array de itens de navegação (Estilo Instagram/App nativo)
  const navItems = [
    {
      label: 'Início',
      href: '/',
      icon: (isActive: boolean) => (
        <svg className="w-6 h-6" fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? "1" : "2"}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      )
    },
    {
      label: 'Explorar',
      href: '/search',
      icon: (isActive: boolean) => (
        <svg className="w-6 h-6" fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? "1" : "2"}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      )
    },
    {
      label: 'Histórico',
      href: '/history',
      icon: (isActive: boolean) => (
        <svg className="w-6 h-6" fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? "1" : "2"}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    },
    {
      label: 'Perfil',
      href: '/profile',
      icon: (isActive: boolean) => (
        <svg className="w-6 h-6" fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? "1" : "2"}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
      )
    }
  ];

  return (
    <div className="md:hidden fixed bottom-0 left-0 w-full z-[100] zen-hide">
      <div className="absolute inset-0 bg-theme-bg/80 backdrop-blur-xl border-t border-theme-border shadow-[0_-10px_40px_rgba(0,0,0,0.2)]"></div>
      
      {/* Container seguro para iPhone notch (env-safe) */}
      <div className="relative px-2 pb-safe pt-2">
        <ul className="flex justify-around items-center">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            
            return (
              <li key={item.label} className="w-16">
                <Link 
                  href={item.href}
                  className={`flex flex-col items-center justify-center gap-1 py-2 w-full transition-all duration-300 ${isActive ? 'text-theme-accent scale-110' : 'text-slate-500 hover:text-slate-300'}`}
                >
                  <div className="relative">
                    {item.icon(isActive)}
                    {isActive && (
                      <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-1 h-1 bg-theme-accent rounded-full shadow-[0_0_8px_rgba(var(--theme-accent-rgb),0.8)]"></span>
                    )}
                  </div>
                  <span className={`text-[9px] font-bold tracking-wide transition-all ${isActive ? 'opacity-100' : 'opacity-0 h-0 overflow-hidden'}`}>
                    {item.label}
                  </span>
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
