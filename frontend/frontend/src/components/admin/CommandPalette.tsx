'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CommandPalette() {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const router = useRouter();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const triggerGhostComments = async () => {
    try {
      const res = await fetch('/api/cron/simulate-comments?token=secret-cron');
      const json = await res.json();
      if (json.success) {
        showToast('success', `👻 Comentário Fantasma gerado com sucesso no Post ID: ${json.postId}`);
      } else {
        showToast('error', `Erro na síntese neural: ${json.error}`);
      }
    } catch (e) {
      showToast('error', 'Falha na API de engajamento fantasma.');
    }
  };

  const executeCommand = (cmd: any) => {
    if (cmd.action === 'triggerGhostComments') {
      triggerGhostComments();
    } else {
      setIsOpen(false);
      if (cmd.href) {
        router.push(cmd.href);
      } else if (cmd.url) {
        router.push(cmd.url);
      }
    }
  };

  const commands = [
    { name: 'Cérebro Autônomo (Fase 132)', url: '/admin/autonomous', icon: '🧠' },
    { name: 'Sinapses & SEO (Fase 133)', url: '/admin/synapses', icon: '🕸️' },
    { name: 'Sistema Imune (Fase 134)', url: '/admin/immune', icon: '🛡️' },
    { name: 'Gênese & Nichos (Fase 135)', url: '/admin/genesis', icon: '🌟' },
    { name: 'Sistema Endócrino (Fase 136)', url: '/admin/endocrine', icon: '⚗️' },
    { name: 'Telemetria Cross-Channel (Fase 137)', url: '/admin/crosschannel', icon: '📡' },
    { name: 'Oráculo Preditor (Fase 138)', url: '/admin/trend', icon: '🔮' },
    { name: 'Auto-Healer SEO (Fase 139)', url: '/admin/seohealer', icon: '🛠️' },
    { name: 'Dashboard Global', url: '/admin', icon: '📊' },
    { id: 'kanban', name: 'Quadro de Pautas', icon: '📋', href: '/admin/tasks', section: 'Redação' },
    { name: 'Redigir Novo Artigo', url: '/admin/posts/new', icon: '✍️' },
    { name: 'Gerenciar Artigos', url: '/admin/posts', icon: '📝' },
    { name: 'Terminal Hacker', url: '/admin/console', icon: '🖥️' },
    { name: 'Base de Leads', url: '/admin/leads', icon: '📬' },
    { id: 'comments', name: 'Ativar Motor Fantasma (Social Proof)', icon: '👻', action: 'triggerGhostComments', section: 'Marketing' },
    { id: 'settings', name: 'Configurações Globais', icon: '⚙️', href: '/admin/settings', section: 'Sistema' },
    { name: 'Oráculo de Pautas', url: '/admin/planner', icon: '🔮' },
    { name: 'Galeria de Mídia', url: '/admin/media', icon: '🖼️' },
    { name: 'CRM Automático', url: '/admin/newsletter', icon: '✉️' },
    { name: 'Automonetizador', url: '/admin/affiliates', icon: '💰' },
  ];

  const filtered = commands.filter((c) => c.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <>
      {/* TOAST EXECUTIVO FLUTUANTE */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/90 border-red-500/50 text-red-300'
          }`}
        >
          <span className="text-lg">{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span className="text-xs font-semibold">{toast.message}</span>
          <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      {isOpen && (
        <div
          className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200"
          onClick={() => setIsOpen(false)}
        >
          <div
            className="bg-slate-900 border border-slate-700/80 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden animate-in slide-in-from-top-4 duration-300 relative"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center px-4 py-4 border-b border-slate-800">
              <svg className="w-6 h-6 text-cyan-500 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <input
                type="text"
                autoFocus
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Digite um comando ou busque uma página..."
                className="w-full bg-transparent text-white text-lg focus:outline-none placeholder:text-slate-500"
              />
              <div className="text-[10px] text-slate-500 font-mono bg-slate-800 px-2 py-1 rounded">ESC</div>
            </div>

            <div className="max-h-[40vh] overflow-y-auto p-2 custom-scrollbar">
              {filtered.length === 0 ? (
                <div className="p-8 text-center text-slate-500 font-bold">Nenhum comando encontrado.</div>
              ) : (
                filtered.map((cmd, i) => (
                  <button
                    key={i}
                    onClick={() => executeCommand(cmd)}
                    className="w-full text-left px-4 py-3 rounded-xl hover:bg-cyan-900/30 hover:text-cyan-400 text-slate-300 font-bold transition-colors flex items-center gap-3 group"
                  >
                    <span className="text-2xl group-hover:scale-110 transition-transform">{cmd.icon}</span>
                    <span>{cmd.name}</span>
                    <span className="ml-auto text-[10px] uppercase tracking-widest text-slate-600 group-hover:text-cyan-600 font-mono">
                      Executar
                    </span>
                  </button>
                ))
              )}
            </div>
            <div className="bg-slate-950 px-4 py-3 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-1">
                  <span className="bg-slate-800 px-1.5 rounded text-white">↑</span>
                  <span className="bg-slate-800 px-1.5 rounded text-white">↓</span> Navegar
                </span>
                <span className="flex items-center gap-1">
                  <span className="bg-slate-800 px-1.5 rounded text-white">↵</span> Selecionar
                </span>
              </div>
              <span className="font-bold text-cyan-800 uppercase tracking-widest text-[9px]">Apollo OS Command</span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
