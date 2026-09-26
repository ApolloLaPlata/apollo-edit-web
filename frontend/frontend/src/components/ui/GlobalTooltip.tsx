'use client';
import { useEffect, useState } from 'react';

export default function GlobalTooltip() {
  const [tooltip, setTooltip] = useState({ text: '', x: 0, y: 0, visible: false });

  useEffect(() => {
    // Desativa tooltips em dispositivos móveis
    if (typeof window !== 'undefined' && window.innerWidth < 768) return;

    const handleMouseOver = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target || !target.closest) return;
      
      const element = target.closest('[title], [data-tooltip]') as HTMLElement;
      
      if (element) {
        const text = element.getAttribute('title') || element.getAttribute('data-tooltip');
        if (!text) return;
        
        // Remove o title nativo para o browser não exibir a tooltip genérica
        if (element.hasAttribute('title')) {
          element.setAttribute('data-tooltip', text);
          element.removeAttribute('title');
        }

        const rect = element.getBoundingClientRect();
        
        setTooltip({
          text,
          x: rect.left + (rect.width / 2),
          y: rect.top - 8, // 8px acima do elemento
          visible: true
        });
      }
    };

    const handleMouseOut = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (!target || !target.closest) return;
      
      const element = target.closest('[data-tooltip]') as HTMLElement;
      if (element) {
        setTooltip(prev => ({ ...prev, visible: false }));
      }
    };

    // Fechar ao rolar a página para não ficar flutuando errado
    const handleScroll = () => {
      setTooltip(prev => ({ ...prev, visible: false }));
    };

    document.addEventListener('mouseover', handleMouseOver);
    document.addEventListener('mouseout', handleMouseOut);
    document.addEventListener('scroll', handleScroll, { passive: true });

    return () => {
      document.removeEventListener('mouseover', handleMouseOver);
      document.removeEventListener('mouseout', handleMouseOut);
      document.removeEventListener('scroll', handleScroll);
    };
  }, []);

  if (!tooltip.visible || !tooltip.text) return null;

  return (
    <div 
      className="fixed z-[9999] px-3 py-1.5 text-[11px] font-bold tracking-wide text-white bg-slate-900 border border-slate-700/50 shadow-2xl rounded-lg pointer-events-none transform -translate-x-1/2 -translate-y-full glass-panel"
      style={{ 
        left: tooltip.x, 
        top: tooltip.y,
        animation: 'tooltipFade 0.2s cubic-bezier(0.16, 1, 0.3, 1) forwards'
      }}
    >
      {tooltip.text}
      
      {/* Triângulo (Seta) */}
      <div 
        className="absolute top-full left-1/2 -translate-x-1/2 w-0 h-0"
        style={{
          borderLeft: '6px solid transparent',
          borderRight: '6px solid transparent',
          borderTop: '6px solid rgba(15, 23, 42, 0.95)' // bg-slate-900
        }}
      ></div>

      <style dangerouslySetInnerHTML={{__html: `
        @keyframes tooltipFade {
          0% { opacity: 0; transform: translate(-50%, calc(-100% + 4px)) scale(0.95); }
          100% { opacity: 1; transform: translate(-50%, -100%) scale(1); }
        }
      `}} />
    </div>
  );
}
