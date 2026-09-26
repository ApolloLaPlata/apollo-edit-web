'use client';
import React, { useEffect } from 'react';

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error("Admin Dashboard Error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center h-full bg-slate-900 text-slate-300 min-h-[50vh] p-4">
      <div className="bg-slate-800/50 backdrop-blur-md border border-red-500/30 rounded-2xl p-8 max-w-md w-full text-center shadow-lg">
        <div className="w-16 h-16 bg-red-500/10 rounded-xl flex items-center justify-center mx-auto mb-5 border border-red-500/20 text-red-500">
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
        </div>
        <h2 className="text-xl font-bold uppercase tracking-widest text-white mb-2">Erro Interno</h2>
        <p className="text-slate-400 text-xs mb-6 leading-relaxed">
          O módulo administrativo encontrou um problema ao renderizar a página.
        </p>
        
        <button
          onClick={() => reset()}
          className="bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-slate-500 font-bold py-2.5 px-6 rounded-lg transition-all w-full text-sm flex items-center justify-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          Recarregar Módulo
        </button>
      </div>
    </div>
  );
}
