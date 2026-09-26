'use client';

import { useState } from 'react';

export default function NewsletterWidget({ blogId, domain }: { blogId?: string; domain?: string }) {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

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
        setMessage(data.message || 'Inscrição realizada com sucesso!');
        setEmail('');
      } else {
        setStatus('error');
        setMessage(data.error || 'Erro ao se inscrever.');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Erro de conexão.');
    }
  };

  return (
    <div className="bg-theme-surface/70 backdrop-blur-2xl border border-theme-border/60 rounded-3xl p-8 shadow-2xl mb-8 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-theme-accent/5 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none group-hover:bg-theme-accent/10 transition-colors" />
      <h3 className="text-2xl font-black text-theme-text mb-3 flex items-center gap-3 relative z-10">
        <span className="text-theme-accent text-3xl">✉️</span> Newsletter Neural
      </h3>
      <p className="text-theme-muted text-sm mb-6 font-medium relative z-10">Receba análises premium, relatórios e as tendências do mercado diretamente no seu inbox. Assinatura VIP 100% gratuita.</p>
      
      <form onSubmit={handleSubmit} className="flex flex-col gap-4 relative z-10">
        <input 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Seu melhor e-mail corporativo..."
          required
          className="bg-black/40 border border-theme-border/80 rounded-xl px-5 py-3.5 text-theme-text text-sm font-semibold focus:outline-none focus:border-theme-accent focus:shadow-[0_0_15px_rgba(var(--accent-rgb),0.3)] transition-all w-full placeholder:text-theme-muted/50"
        />
        <button 
          type="submit" 
          disabled={status === 'loading'}
          className="bg-theme-accent hover:bg-theme-accent-hover text-white font-black py-3.5 px-4 rounded-xl transition-all disabled:opacity-50 shadow-lg shadow-theme-accent/20 uppercase tracking-widest text-[10px]"
        >
          {status === 'loading' ? 'Criptografando & Enviando...' : 'Assinar Acesso VIP'}
        </button>
      </form>
      
      {status === 'success' && <p className="text-emerald-400 font-bold text-sm mt-4 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20">{message}</p>}
      {status === 'error' && <p className="text-red-400 font-bold text-sm mt-4 bg-red-500/10 p-3 rounded-xl border border-red-500/20">{message}</p>}
    </div>
  );
}
