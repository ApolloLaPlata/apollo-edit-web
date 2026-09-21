'use client';
import React, { useState, useEffect } from 'react';

export default function SensitiveContentBlocker({ 
  isSensitive, 
  children 
}: { 
  isSensitive: boolean, 
  children: React.ReactNode 
}) {
  const [unlocked, setUnlocked] = useState(false);
  const [hasMounted, setHasMounted] = useState(false);

  useEffect(() => {
    setHasMounted(true);
    // Verifica se o usuário já aceitou ver conteúdo sensível nesta sessão
    if (sessionStorage.getItem('apollo_nsfw_accepted') === 'true') {
      setUnlocked(true);
    }
  }, []);

  const handleUnlock = () => {
    setUnlocked(true);
    sessionStorage.setItem('apollo_nsfw_accepted', 'true');
  };

  // Se não montou ainda, ou não é sensível, ou já liberou
  if (!isSensitive || unlocked) {
    return <>{children}</>;
  }

  // Apenas renderiza o blocker quando o componente está montado no client, para evitar hydration mismatch de estados locais
  if (!hasMounted) {
    return <div className="min-h-[400px] animate-pulse bg-slate-800/20 rounded-2xl w-full"></div>;
  }

  return (
    <div className="relative rounded-2xl overflow-hidden mb-12 border border-red-500/20">
      {/* Conteúdo Borrado */}
      <div className="blur-xl select-none pointer-events-none opacity-30 h-[500px] overflow-hidden grayscale">
         {children}
      </div>
      
      <div className="absolute inset-0 bg-theme-bg/80 backdrop-blur-xl z-20 flex flex-col items-center justify-center text-center p-8">
         <div className="w-24 h-24 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center text-5xl mb-6 border border-red-500/30 shadow-[0_0_40px_rgba(239,68,68,0.2)] animate-pulse">
            ⚠️
         </div>
         <h3 className="text-3xl md:text-4xl font-black text-theme-text mb-3 tracking-tight">Conteúdo Sensível</h3>
         <p className="text-slate-400 mb-8 max-w-lg font-medium text-lg leading-relaxed">
           A Inteligência Artificial sinalizou que esta matéria contém material impróprio para menores, cenas fortes ou relatos perturbadores.
         </p>
         
         <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
           <button 
             onClick={handleUnlock}
             className="flex-1 bg-red-600 hover:bg-red-500 text-white font-black px-6 py-4 rounded-xl transition-all shadow-[0_0_20px_rgba(220,38,38,0.4)] hover:shadow-[0_0_30px_rgba(220,38,38,0.6)] hover:-translate-y-1 uppercase tracking-widest text-[11px]"
           >
             Sou Maior e Aceito Ver
           </button>
           <a 
             href="/" 
             className="flex-1 bg-slate-800 hover:bg-slate-700 text-white font-black px-6 py-4 rounded-xl transition-all border border-slate-700 flex items-center justify-center uppercase tracking-widest text-[11px]"
           >
             Sair em Segurança
           </a>
         </div>
      </div>
    </div>
  );
}
