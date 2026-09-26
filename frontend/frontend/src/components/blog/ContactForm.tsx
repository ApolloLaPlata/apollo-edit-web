'use client';
import React, { useState } from 'react';

export default function ContactForm({ domain }: { domain: string }) {
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get('name'),
      email: formData.get('email'),
      message: formData.get('message'),
      domain: domain
    };

    try {
      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      
      const result = await res.json();
      
      if (res.ok) {
        setSuccess(true);
        (e.target as HTMLFormElement).reset();
      } else {
        setError(result.error || 'Ocorreu um erro ao enviar a mensagem.');
      }
    } catch (err) {
      setError('Falha na comunicação com o servidor.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-900/40 p-8 rounded-3xl border border-slate-800 space-y-4 relative overflow-hidden">
      {success && (
        <div className="absolute inset-0 bg-emerald-900/90 backdrop-blur-md flex flex-col items-center justify-center z-10 animate-in fade-in zoom-in duration-300">
          <svg className="w-16 h-16 text-emerald-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <h3 className="text-xl font-black text-white">Mensagem Recebida!</h3>
          <p className="text-sm text-emerald-200 mt-2">Nossa redação entrará em contato em breve.</p>
          <button type="button" onClick={() => setSuccess(false)} className="mt-6 text-xs uppercase font-bold text-white/50 hover:text-white">Enviar outra mensagem</button>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/50 text-red-400 text-sm p-4 rounded-xl text-center">
          {error}
        </div>
      )}

      <input name="name" type="text" required placeholder="Seu Nome" className="w-full bg-black/50 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-theme-accent" />
      <input name="email" type="email" required placeholder="E-mail de Retorno" className="w-full bg-black/50 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-theme-accent" />
      <textarea name="message" required rows={5} placeholder="Sua Mensagem / Pauta" className="w-full bg-black/50 border border-slate-800 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-theme-accent"></textarea>
      
      <button disabled={loading} type="submit" className={`w-full bg-theme-accent text-black font-black uppercase tracking-widest py-4 rounded-xl transition-all ${loading ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105 shadow-[0_0_20px_rgba(var(--theme-accent-rgb),0.3)]'}`}>
         {loading ? 'Enviando...' : 'Enviar Mensagem'}
      </button>
    </form>
  );
}
