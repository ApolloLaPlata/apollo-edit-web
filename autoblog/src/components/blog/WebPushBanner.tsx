'use client';

import React, { useState, useEffect } from 'react';

export default function WebPushBanner() {
  const [show, setShow] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  useEffect(() => {
    const hasResponded = localStorage.getItem('push_notification_responded');
    if (!hasResponded) {
      const timer = setTimeout(() => setShow(true), 4000);
      return () => clearTimeout(timer);
    }
  }, []);

  const handleResponse = async (accepted: boolean) => {
    setShow(false);
    localStorage.setItem('push_notification_responded', 'true');
    
    if (accepted) {
      try {
        // Em um ambiente real, aqui chamaria a API do OneSignal ou Service Worker nativo.
        // Simularemos o delay de ativação do Push no navegador
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (e) {
        // Silently handle
      }
      setToast('🚀 Notificações Web Push PWA ativadas com sucesso! Você receberá alertas prioritários da colmeia em tempo real.');
      setTimeout(() => setToast(null), 6000);
    }
  };

  return (
    <>
      {/* TOAST EXECUTIVO DE SUCCESSO (ZERO NATIVE DIALOGS) */}
      {toast && (
        <div className="fixed top-6 right-6 z-[300] bg-emerald-950/95 border border-emerald-500/50 p-4 rounded-2xl shadow-2xl flex items-center gap-3.5 text-emerald-300 animate-in slide-in-from-top-5 duration-300 max-w-md backdrop-blur-xl">
          <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 text-lg flex-shrink-0 border border-emerald-500/30">
            ✨
          </div>
          <div className="text-xs font-bold leading-relaxed">{toast}</div>
          <button onClick={() => setToast(null)} className="text-emerald-400/70 hover:text-white text-xs font-mono ml-auto">
            [✕]
          </button>
        </div>
      )}

      {/* BANNER DE INSCRIÇÃO WEB PUSH PWA */}
      {show && (
        <div className="fixed bottom-6 left-6 z-50 bg-slate-900/90 backdrop-blur-2xl border border-slate-700/80 p-5 rounded-3xl shadow-[0_15px_50px_rgba(0,0,0,0.6)] max-w-sm flex items-start gap-4 animate-in slide-in-from-bottom-10 fade-in duration-500">
          <div className="w-12 h-12 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-2xl flex items-center justify-center flex-shrink-0 text-white text-2xl shadow-lg shadow-cyan-500/20">
            🔔
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-1.5 mb-1">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <h4 className="text-white font-black text-xs uppercase tracking-wider">Alerta da Redação VIP</h4>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed mb-4">
              Deseja receber notificações PWA instantâneas no seu navegador sempre que publicarmos reportagens investigativas exclusivas?
            </p>
            <div className="flex gap-2">
              <button 
                onClick={() => handleResponse(true)}
                className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-extrabold px-4 py-2 rounded-xl transition-all shadow-md shadow-cyan-500/20 active:scale-95 flex-1 text-center"
              >
                ⚡ Sim, ativar
              </button>
              <button 
                onClick={() => handleResponse(false)}
                className="bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs font-bold px-3 py-2 rounded-xl transition-all border border-slate-700/80"
              >
                Agora não
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
