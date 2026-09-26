import React from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Acesso VIP | Portal Exclusivo',
  description: 'Faça login para desbloquear matérias e análises exclusivas.',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 relative overflow-hidden px-4">
      {/* Background Cinematográfico */}
      <div className="absolute inset-0 bg-[url('https://images.pexels.com/photos/547116/pexels-photo-547116.jpeg?auto=compress&cs=tinysrgb&w=1920')] bg-cover bg-center opacity-10" />
      <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/80 to-transparent" />
      <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-theme-accent/5 rounded-full blur-[100px]" />

      <div className="w-full max-w-md z-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
        
        {/* Brand Header */}
        <div className="text-center mb-8">
           <Link href="/" className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 shadow-2xl mb-4 group hover:scale-105 transition-transform">
              <span className="text-2xl font-black text-theme-accent group-hover:drop-shadow-[0_0_15px_rgba(255,255,255,0.5)] transition-all">VIP</span>
           </Link>
           <h1 className="text-3xl font-black text-white tracking-tight">Portal do Assinante</h1>
           <p className="text-slate-400 font-medium text-sm mt-2">Acesso irrestrito a reportagens e análises profundas.</p>
        </div>

        {/* Formulário Glassmorphism */}
        <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-3xl p-8 shadow-2xl">
          <form className="space-y-6">
            <div className="space-y-2">
              <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Seu E-mail Cadastrado</label>
              <input 
                type="email" 
                placeholder="nome@email.com" 
                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl p-3.5 text-white font-medium focus:border-theme-accent focus:ring-1 focus:ring-theme-accent transition-all outline-none"
              />
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                 <label className="text-[10px] font-black uppercase tracking-widest text-slate-500">Senha de Acesso</label>
                 <a href="#" className="text-[10px] text-theme-accent font-bold hover:underline">Esqueceu?</a>
              </div>
              <input 
                type="password" 
                placeholder="••••••••" 
                className="w-full bg-slate-950/50 border border-slate-800 rounded-xl p-3.5 text-white font-medium focus:border-theme-accent focus:ring-1 focus:ring-theme-accent transition-all outline-none"
              />
            </div>

            <button 
              type="button" 
              className="w-full py-4 rounded-xl bg-theme-accent text-black font-black uppercase tracking-widest text-xs hover:bg-theme-accent-hover transition-colors shadow-[0_0_20px_rgba(255,255,255,0.1)] hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] mt-2"
            >
              Desbloquear Acesso
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-slate-800 text-center">
             <p className="text-xs text-slate-400">
               Ainda não faz parte do clube VIP? <a href="#" className="text-theme-accent font-bold hover:underline">Assine gratuitamente</a>
             </p>
          </div>
        </div>
        
        {/* Segurança */}
        <div className="mt-8 text-center flex items-center justify-center gap-2 text-slate-500 text-[10px] uppercase font-bold tracking-widest">
           <span>🔒</span> Criptografia de Ponta a Ponta
        </div>

      </div>
    </div>
  );
}
