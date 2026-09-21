import React from 'react';
import Link from 'next/link';

export const metadata = {
  title: 'Nova Story | CMS Admin',
};

export default function NewStoryPage() {
  // Nota: Como o app router mistura server-components, esse form poderia ser um Client Component
  // ou usar Next.js Server Actions para fazer a ingestão no SQLite. 
  // O layout aqui é um wireframe robusto do formulário no padrão VIP VIP Admin.
  
  return (
    <div className="p-6 md:p-10 space-y-8 bg-slate-950 min-h-screen text-slate-200">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <Link href="/admin/stories" className="text-xs text-theme-accent font-bold uppercase tracking-widest hover:underline mb-2 block">
            ← Voltar para Stories
          </Link>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight flex items-center gap-3">
            Injeção de Nova Mídia
          </h1>
          <p className="text-slate-400 mt-2 text-sm font-medium">Cadastre um vídeo curto ou imagem vertical para o Motor Viral.</p>
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl backdrop-blur-md max-w-4xl">
        <form className="p-8 md:p-12 space-y-8">
          
          <div className="space-y-2">
             <label className="text-xs font-black uppercase tracking-widest text-slate-500 block">Manchete / Hook (Título)</label>
             <input 
               type="text" 
               placeholder="Ex: O Segredo Obscuro da IA..." 
               className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-white font-bold focus:border-theme-accent focus:ring-1 focus:ring-theme-accent transition-all outline-none"
             />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
             <div className="space-y-2">
                <label className="text-xs font-black uppercase tracking-widest text-slate-500 block">URL do Vídeo (MP4)</label>
                <input 
                  type="text" 
                  placeholder="https://sua-cloud.com/video.mp4" 
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-300 focus:border-theme-accent transition-all outline-none"
                />
             </div>
             <div className="space-y-2">
                <label className="text-xs font-black uppercase tracking-widest text-slate-500 block">Imagem de Capa (Poster)</label>
                <input 
                  type="text" 
                  placeholder="https://sua-cloud.com/poster.jpg" 
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm text-slate-300 focus:border-theme-accent transition-all outline-none"
                />
             </div>
          </div>

          <div className="space-y-2">
             <label className="text-xs font-black uppercase tracking-widest text-slate-500 block">Conteúdo Escrito (Resumo Dinâmico)</label>
             <textarea 
               rows={4}
               placeholder="Escreva a descrição do conteúdo que aparecerá sob a manchete..." 
               className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-sm font-medium text-slate-300 focus:border-theme-accent transition-all outline-none resize-none"
             ></textarea>
          </div>

          <div className="pt-6 border-t border-slate-800 flex justify-end gap-4">
            <Link 
              href="/admin/stories"
              className="px-6 py-4 rounded-xl border border-slate-700 text-slate-400 font-bold uppercase tracking-widest text-xs hover:bg-slate-800 transition-colors"
            >
              Cancelar
            </Link>
            <button 
              type="button" 
              className="px-10 py-4 rounded-xl bg-gradient-to-r from-theme-accent to-blue-500 text-black font-black uppercase tracking-widest text-xs shadow-[0_0_30px_rgba(6,182,212,0.4)] hover:shadow-[0_0_50px_rgba(6,182,212,0.6)] hover:scale-105 transition-all"
            >
              Injetar Story no Motor
            </button>
          </div>

        </form>
      </div>
    </div>
  );
}
