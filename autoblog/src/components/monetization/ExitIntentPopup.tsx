'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

/**
 * Motor Exit-Intent (A Armadilha de Fuga)
 * Monitora o cursor do usuário. Se ele jogar o mouse pro topo da tela 
 * (tentando fechar a aba), a tela escurece e joga uma oferta de Afiliado matadora.
 */
export default function ExitIntentPopup({ offerLink, offerTitle }: { offerLink: string, offerTitle: string }) {
  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    // Evita encher o saco de quem já recusou (cookie de 1 dia)
    if (typeof window !== 'undefined') {
      const hasSeenPopup = sessionStorage.getItem('exit_intent_seen');
      if (hasSeenPopup === 'true') return;
    }

    const mouseOutHandler = (e: MouseEvent) => {
      // Se o mouse passar pelo topo da janela (y < 20px) num desktop
      if (e.clientY < 20) {
        setShowPopup(true);
        sessionStorage.setItem('exit_intent_seen', 'true');
        // Desativa o listener após mostrar uma vez
        document.removeEventListener('mouseout', mouseOutHandler);
      }
    };

    // Delay de 5 segundos para não disparar se ele abrir a aba e sair correndo
    const timer = setTimeout(() => {
      document.addEventListener('mouseout', mouseOutHandler);
    }, 5000);

    return () => {
      clearTimeout(timer);
      document.removeEventListener('mouseout', mouseOutHandler);
    };
  }, []);

  if (!showPopup) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay Escuro com Animação */}
      <div 
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-300"
        onClick={() => setShowPopup(false)}
      />
      
      {/* Caixa do PopUp */}
      <div className="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-8 md:p-12 rounded-3xl shadow-2xl max-w-lg w-full text-center animate-in zoom-in-95 duration-500">
        
        {/* Botão Fechar Invisível */}
        <button 
          onClick={() => setShowPopup(false)}
          className="absolute top-4 right-4 text-slate-400 hover:text-slate-900 dark:hover:text-white"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
        </button>

        <span className="text-6xl mb-6 block drop-shadow-md">🎁</span>
        
        <h2 className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-4 leading-tight tracking-tight">
          Espera! Não vá embora ainda...
        </h2>
        
        <p className="text-slate-600 dark:text-slate-400 mb-8 font-medium">
          Temos uma oferta secreta e exclusiva que a maioria dos leitores nunca vai ver. Você quer conferir?
        </p>

        <div className="flex flex-col gap-3">
          <Link 
            href={offerLink}
            target="_blank"
            rel="noopener noreferrer"
            onClick={() => setShowPopup(false)}
            className="w-full bg-red-600 hover:bg-red-500 text-white font-black py-5 rounded-xl uppercase tracking-widest text-sm transition-all shadow-[0_10px_20px_rgba(220,38,38,0.3)] hover:shadow-[0_15px_30px_rgba(220,38,38,0.4)] hover:-translate-y-1"
          >
            🔥 {offerTitle}
          </Link>
          
          <button 
            onClick={() => setShowPopup(false)}
            className="w-full py-4 text-xs font-bold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 uppercase tracking-wider transition-colors"
          >
            Não, obrigado. Eu odeio ofertas.
          </button>
        </div>

      </div>
    </div>
  );
}
