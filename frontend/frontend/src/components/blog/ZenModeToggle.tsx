'use client';
import React, { useEffect, useState } from 'react';

export default function ZenModeToggle() {
  const [zenMode, setZenMode] = useState(false);

  useEffect(() => {
    if (zenMode) {
      document.body.classList.add('zen-mode');
    } else {
      document.body.classList.remove('zen-mode');
    }
  }, [zenMode]);

  return (
    <button 
      onClick={() => setZenMode(!zenMode)}
      className="flex items-center gap-2 bg-theme-surface/80 hover:bg-theme-surface border border-theme-border px-3 py-1.5 rounded-full text-xs font-semibold text-theme-muted hover:text-theme-accent transition-all shadow-sm"
      title="Ativar/Desativar Leitor Focado"
    >
      {zenMode ? (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"></path></svg>
          Sair do Modo Zen
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
          Leitor Focado
        </>
      )}
    </button>
  );
}
