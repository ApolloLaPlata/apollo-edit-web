'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from '@/components/ui/Toast';

export default function ContextMenu() {
  const [menuData, setMenuData] = useState({ visible: false, x: 0, y: 0 });
  const router = useRouter();

  useEffect(() => {
    // Apenas desktop
    if (typeof window !== 'undefined' && window.innerWidth < 768) return;

    const handleContextMenu = (e: MouseEvent) => {
      // Escape hatch: Se segurar Shift, mostra o menu nativo do sistema
      if (e.shiftKey) return;

      e.preventDefault();

      const { clientX: x, clientY: y } = e;
      
      // Prevenir que o menu vaze para fora da tela (direita/baixo)
      const menuWidth = 220; // Aproximado
      const menuHeight = 250; // Aproximado
      
      const adjustedX = x + menuWidth > window.innerWidth ? window.innerWidth - menuWidth - 10 : x;
      const adjustedY = y + menuHeight > window.innerHeight ? window.innerHeight - menuHeight - 10 : y;

      setMenuData({ visible: true, x: adjustedX, y: adjustedY });
    };

    const handleClick = () => {
      if (menuData.visible) setMenuData({ ...menuData, visible: false });
    };

    const handleScroll = () => {
      if (menuData.visible) setMenuData({ ...menuData, visible: false });
    };

    document.addEventListener('contextmenu', handleContextMenu);
    document.addEventListener('click', handleClick);
    document.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('click', handleClick);
      document.removeEventListener('scroll', handleScroll);
    };
  }, [menuData]);

  if (!menuData.visible) return null;

  const handleCopySelection = () => {
    const text = window.getSelection()?.toString();
    if (text) {
      navigator.clipboard.writeText(text);
      toast.success('Texto copiado com sucesso!');
    } else {
      toast.info('Nenhum texto selecionado para copiar.');
    }
  };

  const handleCopyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    toast.success('Link da página copiado!');
  };

  const handleZenMode = () => {
    const isZen = document.body.classList.contains('zen-mode');
    if (isZen) {
      document.body.classList.remove('zen-mode');
      toast.info('Modo Zen Desativado');
    } else {
      document.body.classList.add('zen-mode');
      toast.success('Modo Zen Ativado');
    }
  };

  return (
    <div 
      className="fixed z-[99999] bg-theme-surface/95 backdrop-blur-xl border border-theme-border rounded-xl shadow-2xl py-2 flex flex-col min-w-[220px] animate-fade-in-up"
      style={{ left: menuData.x, top: menuData.y, animationDuration: '0.2s' }}
      onContextMenu={(e) => e.preventDefault()} // Impede abrir de novo em cima dele
    >
      <div className="px-3 pb-2 mb-1 border-b border-theme-border/50 text-[10px] font-black uppercase tracking-[0.2em] text-theme-muted">
        Ações
      </div>

      <button onClick={() => router.back()} className="w-full text-left px-4 py-2 text-sm font-semibold text-theme-text hover:bg-white/5 transition-colors flex items-center justify-between group">
        <span>Página Anterior</span>
        <span className="text-theme-muted group-hover:text-theme-text transition-colors text-xs opacity-60">Alt+←</span>
      </button>

      <button onClick={() => router.push('/')} className="w-full text-left px-4 py-2 text-sm font-semibold text-theme-text hover:bg-white/5 transition-colors flex items-center justify-between">
        <span>Ir para Início</span>
      </button>

      <div className="my-1 border-t border-theme-border/50"></div>

      <button onClick={handleCopySelection} className="w-full text-left px-4 py-2 text-sm font-semibold text-theme-text hover:bg-white/5 transition-colors flex items-center justify-between group">
        <span>Copiar Seleção</span>
        <span className="text-theme-muted group-hover:text-theme-text transition-colors text-xs opacity-60">Ctrl+C</span>
      </button>

      <button onClick={handleCopyLink} className="w-full text-left px-4 py-2 text-sm font-semibold text-theme-text hover:bg-white/5 transition-colors flex items-center justify-between">
        <span>Copiar Link da Página</span>
      </button>

      <div className="my-1 border-t border-theme-border/50"></div>

      <button onClick={handleZenMode} className="w-full text-left px-4 py-2 text-sm font-semibold text-theme-accent hover:bg-theme-accent hover:text-white transition-colors flex items-center justify-between group">
        <span>Alternar Modo Zen</span>
        <span className="opacity-0 group-hover:opacity-100 transition-opacity">👁️</span>
      </button>
    </div>
  );
}
