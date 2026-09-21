import React from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Meu Painel | Portal Exclusivo',
};

export default function UserProfilePage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200">
      
      {/* Header do Usuário */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-12 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-full h-full bg-theme-accent/5 pointer-events-none opacity-50" />
        
        <div className="max-w-5xl mx-auto relative z-10 flex flex-col md:flex-row items-center gap-6">
          <div className="w-24 h-24 rounded-full bg-slate-800 border-4 border-slate-700 flex items-center justify-center text-3xl font-black text-slate-400 overflow-hidden shadow-2xl">
            {/* Imagem de perfil dinâmica no futuro */}
            JD
          </div>
          <div className="text-center md:text-left">
            <div className="inline-flex items-center gap-2 mb-2">
               <span className="px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest bg-theme-accent text-black">Membro VIP</span>
               <span className="text-xs text-slate-500 font-medium tracking-wide">Assinante desde Jul 2026</span>
            </div>
            <h1 className="text-3xl font-black text-white tracking-tight">John Doe Silva</h1>
            <p className="text-slate-400 font-medium text-sm">john.doe@email.com</p>
          </div>
          
          <div className="md:ml-auto mt-4 md:mt-0">
             <Link href="/" className="px-6 py-2.5 rounded-full border border-slate-700 text-xs font-bold text-slate-300 hover:bg-slate-800 transition-colors mr-3">Configurações</Link>
             <button className="px-6 py-2.5 rounded-full border border-red-900/30 text-xs font-bold text-red-500 hover:bg-red-900/20 transition-colors">Sair</button>
          </div>
        </div>
      </div>

      {/* Conteúdo do Dashboard (Artigos Salvos & Recentes) */}
      <div className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-10">
         
         <div className="md:col-span-2 space-y-8">
            <div>
               <h2 className="text-xl font-black text-white mb-6 flex items-center gap-2">
                  <span className="text-theme-accent">🔖</span> Sua Biblioteca Salva
               </h2>
               
               <div className="space-y-4">
                  {/* Lista mockada de artigos salvos */}
                  {[1,2,3].map(i => (
                    <div key={i} className="group p-5 bg-slate-900/40 border border-slate-800/80 rounded-2xl flex gap-5 hover:bg-slate-800/40 transition-colors cursor-pointer shadow-lg">
                      <div className="w-24 h-24 bg-slate-800 rounded-xl flex-shrink-0 overflow-hidden relative border border-slate-700">
                         {/* eslint-disable-next-line @next/next/no-img-element */}
                         <img src={`https://images.pexels.com/photos/${1000000 + i}/pexels-photo-${1000000 + i}.jpeg?auto=compress&cs=tinysrgb&w=150`} alt="thumb" className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                      </div>
                      <div className="flex flex-col justify-center">
                         <span className="text-[10px] text-theme-accent font-black uppercase tracking-widest mb-1">Tecnologia Global</span>
                         <h3 className="text-base font-bold text-slate-200 leading-snug group-hover:text-white transition-colors">O Impacto das Novas Interfaces na Percepção Humana</h3>
                         <p className="text-xs text-slate-500 mt-2 font-medium">Salvo há 2 dias</p>
                      </div>
                    </div>
                  ))}
               </div>
            </div>
         </div>

         {/* Sidebar de Perfil */}
         <div className="space-y-8">
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-3xl p-6 shadow-xl">
               <h3 className="text-sm font-black uppercase tracking-widest text-slate-400 mb-4 border-b border-slate-800 pb-3">Seu Status</h3>
               <div className="space-y-4">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Nível de Leitura</span>
                    <div className="flex items-end gap-2">
                      <span className="text-2xl font-black text-white">Top 5%</span>
                      <span className="text-xs text-emerald-400 font-bold mb-1">↑ Crescendo</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Matérias Lidas</span>
                    <span className="text-xl font-bold text-slate-300">142</span>
                  </div>
               </div>
            </div>

            <div className="bg-gradient-to-br from-theme-accent/20 to-slate-900 border border-theme-accent/30 rounded-3xl p-6 shadow-xl relative overflow-hidden">
               <div className="absolute top-0 right-0 w-20 h-20 bg-theme-accent rounded-full blur-3xl opacity-20 -mr-10 -mt-10" />
               <h3 className="text-sm font-black text-white mb-2 relative z-10">Convide Amigos</h3>
               <p className="text-xs text-slate-300 font-medium leading-relaxed relative z-10 mb-4">Ganhe meses adicionais grátis no painel Premium por cada leitor convidado.</p>
               <button className="w-full py-2.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-xs font-bold transition-colors border border-white/10 relative z-10">
                 Gerar Link Pessoal
               </button>
            </div>
         </div>

      </div>
    </div>
  );
}
