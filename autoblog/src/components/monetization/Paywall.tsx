'use client';

import React, { useState, useEffect } from 'react';

/**
 * Paywall (Muralha de Fogo para Captura de Leads)
 * Sobrepõe a parte inferior do texto com um Blur pesado e força o usuário
 * a fornecer o e-mail ou pagar para continuar a leitura de fofocas premium.
 */
export default function Paywall({ children }: { children: React.ReactNode }) {
  const [unlocked, setUnlocked] = useState(false);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  // Verifica se o usuário já destravou antes (simulando cache ou cookie)
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const isVIP = localStorage.getItem('site_vip_status');
      if (isVIP === 'true') setUnlocked(true);
    }
  }, []);

  const handleUnlock = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.includes('@')) return;
    
    setLoading(true);
    // Simula a requisição pro backend pra salvar o Lead
    setTimeout(() => {
      setLoading(false);
      setUnlocked(true);
      localStorage.setItem('site_vip_status', 'true');
    }, 1500);
  };

  if (unlocked) {
    return <div className="w-full animate-in fade-in duration-700">{children}</div>;
  }

  return (
    <div className="relative w-full">
      {/* Container truncado com Blur */}
      <div className="max-h-[300px] overflow-hidden relative">
        <div className="opacity-40 blur-sm pointer-events-none select-none">
          {children}
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 dark:from-slate-950 dark:via-slate-950/80 to-transparent z-10" />
      </div>

      {/* Caixa de Captura (Paywall) */}
      <div className="absolute bottom-0 left-0 w-full z-20 flex flex-col items-center justify-center pb-8 pt-24 px-4 text-center">
        <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl border border-slate-200 dark:border-slate-700 p-8 md:p-12 rounded-3xl shadow-2xl max-w-lg w-full transform -translate-y-8 animate-in slide-in-from-bottom-10 fade-in duration-500">
          <div className="w-16 h-16 bg-red-600/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_20px_rgba(220,38,38,0.3)]">
            <svg className="w-8 h-8 fill-current" viewBox="0 0 24 24"><path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/></svg>
          </div>
          <h2 className="text-2xl md:text-3xl font-black text-slate-900 dark:text-white mb-2 tracking-tight">
            Conteúdo Exclusivo
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-8 font-medium">
            Assine nossa newsletter gratuita VIP para continuar lendo e acessar a fofoca na íntegra.
          </p>
          
          <form onSubmit={handleUnlock} className="flex flex-col gap-4">
            <input 
              type="email" 
              placeholder="Digite seu melhor e-mail"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-4 bg-slate-100 dark:bg-slate-950 border border-slate-300 dark:border-slate-800 rounded-xl outline-none focus:border-red-500 focus:ring-2 focus:ring-red-500/20 transition-all font-medium text-slate-900 dark:text-white"
            />
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-4 rounded-xl uppercase tracking-wider text-sm transition-all shadow-lg hover:shadow-red-600/30 flex items-center justify-center gap-2"
            >
              {loading ? (
                <span className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
              ) : (
                'Destravar Matéria Agora'
              )}
            </button>
          </form>
          <p className="mt-6 text-[10px] uppercase tracking-widest text-slate-400 font-bold">
            Zero Spam. 100% Notícias Quentes.
          </p>
        </div>
      </div>
    </div>
  );
}
