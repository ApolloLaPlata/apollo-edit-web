'use client';

import React, { useState, useEffect } from 'react';

export default function ExitIntentPopup({ blogId }: { blogId: string }) {
  const [show, setShow] = useState(false);
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

  useEffect(() => {
    // Check if already closed or subscribed
    if (localStorage.getItem(`exit_intent_closed_${blogId}`)) return;

    const handleMouseLeave = (e: MouseEvent) => {
      if (e.clientY <= 0) {
        if (!localStorage.getItem(`exit_intent_closed_${blogId}`)) {
          setShow(true);
          localStorage.setItem(`exit_intent_closed_${blogId}`, 'true');
        }
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    return () => document.removeEventListener('mouseleave', handleMouseLeave);
  }, [blogId]);

  if (!show) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus('loading');
    
    try {
      const res = await fetch('/api/analytics/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, blogId })
      });
      const data = await res.json();
      
      if (data.success) {
        setStatus('success');
        setTimeout(() => setShow(false), 3000);
      } else {
        setStatus('error');
      }
    } catch (err) {
      setStatus('error');
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-300">
      <div className="bg-theme-surface border border-theme-border rounded-3xl p-8 md:p-12 shadow-2xl max-w-lg w-full relative animate-in zoom-in-95 duration-500">
        
        {/* Botão Fechar */}
        <button 
          onClick={() => setShow(false)}
          className="absolute top-4 right-4 text-theme-muted hover:text-white transition-colors p-2"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-theme-accent/20 text-theme-accent rounded-full flex items-center justify-center text-3xl mx-auto mb-4 border border-theme-accent/30 shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.4)]">
            🎁
          </div>
          <h2 className="text-3xl font-black text-theme-text mb-3 tracking-tight">Espere! Não vá ainda...</h2>
          <p className="text-theme-muted font-medium">Junte-se a milhares de leitores que recebem nossas análises exclusivas diretamente no e-mail, antes de todo mundo.</p>
        </div>

        {status === 'success' ? (
          <div className="bg-emerald-500/10 border border-emerald-500/30 p-6 rounded-2xl text-center">
            <span className="text-4xl block mb-2">✅</span>
            <h3 className="text-emerald-400 font-black text-lg">Inscrição Confirmada!</h3>
            <p className="text-emerald-300/80 text-sm mt-1">Bem-vindo(a) ao grupo VIP.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Digite seu melhor e-mail..."
              required
              className="bg-slate-900/50 border border-slate-700/80 rounded-xl px-5 py-4 text-white text-center text-lg focus:outline-none focus:border-theme-accent focus:shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.3)] transition-all"
            />
            <button 
              type="submit" 
              disabled={status === 'loading'}
              className="bg-theme-accent hover:bg-theme-accent-hover text-white font-black py-4 px-6 rounded-xl transition-all shadow-lg shadow-theme-accent/20 uppercase tracking-widest text-sm disabled:opacity-50 mt-2"
            >
              {status === 'loading' ? 'Processando...' : 'QUERO ACESSO VIP'}
            </button>
            {status === 'error' && <p className="text-red-400 text-xs font-bold text-center mt-2">Ocorreu um erro. Tente novamente.</p>}
          </form>
        )}
        
        <div className="text-center mt-6">
          <button onClick={() => setShow(false)} className="text-[10px] uppercase font-bold text-slate-500 hover:text-slate-300 transition-colors tracking-widest">
            Não, obrigado. Prefiro perder as novidades.
          </button>
        </div>
      </div>
    </div>
  );
}
