'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function WorkspaceSwitcher() {
  const [blogs, setBlogs] = useState<any[]>([]);
  const [activeWorkspace, setActiveWorkspace] = useState('global');
  const router = useRouter();

  useEffect(() => {
    // Busca os blogs
    fetch('/api/admin/blogs/list')
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          setBlogs(data.blogs);
        }
      });
      
    // Verifica se já tem um workspace salvo no localStorage
    const saved = localStorage.getItem('apollo_active_workspace');
    if (saved) {
      setActiveWorkspace(saved);
      // Opcional: setar um cookie para que o SSR também saiba (se formos usar SSR no futuro)
      document.cookie = `active_workspace=${saved}; path=/;`;
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setActiveWorkspace(val);
    localStorage.setItem('apollo_active_workspace', val);
    document.cookie = `active_workspace=${val}; path=/;`;
    
    // Força o refresh da página atual para recarregar os dados do painel central
    router.refresh();
  };

  return (
    <div className="mb-6 bg-slate-950/40 backdrop-blur-md rounded-2xl p-4 border border-slate-700/50 shadow-inner group hover:border-cyan-500/30 transition-colors">
      <label className="text-[10px] uppercase tracking-widest text-slate-400 font-black mb-2 flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 group-hover:animate-ping"></span>
        Contexto de Trabalho (Canal)
      </label>
      <select 
        value={activeWorkspace}
        onChange={handleChange}
        className="w-full bg-slate-900/80 border border-slate-600/60 rounded-xl p-3 text-slate-200 outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 text-sm font-bold shadow-lg appearance-none cursor-pointer"
        style={{ backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M6 8l4 4 4-4'/%3e%3c/svg%3e")`, backgroundPosition: `right 0.5rem center`, backgroundRepeat: `no-repeat`, backgroundSize: `1.5em 1.5em`, paddingRight: `2.5rem` }}
      >
        <option value="global">🌐 Visão Global (Todos)</option>
        {blogs.map(b => (
          <option key={b.id} value={b.id}>📺 {b.name}</option>
        ))}
      </select>
    </div>
  );
}
