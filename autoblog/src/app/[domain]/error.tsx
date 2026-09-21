'use client';
import React, { useEffect } from 'react';

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Aqui poderíamos logar para um serviço de telemetria
    console.error("Apollo Engine Error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-theme-bg text-theme-text p-4">
      <div className="bg-theme-surface/70 backdrop-blur-2xl border border-red-500/30 rounded-3xl p-10 max-w-lg w-full text-center shadow-[0_0_50px_rgba(239,68,68,0.1)]">
        <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-500/20">
          <span className="text-4xl">⚠️</span>
        </div>
        <h2 className="text-2xl font-black uppercase tracking-widest text-white mb-4">Falha no Sistema</h2>
        <p className="text-theme-muted font-medium text-sm mb-8 leading-relaxed">
          Ocorreu um erro temporário na renderização desta página. Nossa equipe técnica já foi notificada da falha.
        </p>
        
        <button
          onClick={() => reset()}
          className="bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 hover:border-red-500/50 font-bold py-3 px-8 rounded-xl transition-all w-full uppercase tracking-widest text-xs"
        >
          Tentar Reconectar
        </button>
      </div>
    </div>
  );
}
