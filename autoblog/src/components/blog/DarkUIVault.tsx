'use client';

import React, { useState, useEffect } from 'react';

/**
 * 💀 DARK UI VAULT (Etapas 34 e 35)
 * Uma aba oculta no site para os VIPs que pagam criptomoeda.
 * Contém matérias ultra-pesadas extraídas do Deep Crawler.
 * Modo Snapchat: Tudo aqui se autodestrói em X minutos.
 */
export default function DarkUIVault() {
  const [isUnlocked, setIsUnlocked] = useState(false);
  const [timeLeft, setTimeLeft] = useState(3600); // 60 minutos (Autodestruição)

  useEffect(() => {
    if (isUnlocked && timeLeft > 0) {
      const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
      return () => clearInterval(timer);
    }
  }, [isUnlocked, timeLeft]);

  const unlockVault = () => {
    const password = prompt("DIGITE A SENHA CRIPTOGRÁFICA DO UNDERGROUND:");
    if (password === 'godmode') setIsUnlocked(true);
    else alert("Senha Incorreta. Rastreando IP... (Brincadeira)");
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (!isUnlocked) {
     return (
        <div className="min-h-[400px] flex flex-col items-center justify-center bg-black border-2 border-dashed border-red-900/50 p-8 rounded-2xl mx-auto my-10 max-w-2xl relative overflow-hidden group">
           <div className="absolute inset-0 bg-red-900/10 opacity-0 group-hover:opacity-100 transition-opacity" />
           <span className="text-4xl mb-4">💀</span>
           <h3 className="text-red-500 font-black tracking-[0.2em] text-xl mb-2">A SALA OBSCURA</h3>
           <p className="text-slate-500 text-sm mb-6 text-center">Material sob Sigilo Jurídico. Apenas VIPs (Level 100+).</p>
           <button onClick={unlockVault} className="bg-red-950 border border-red-800 text-red-500 hover:bg-red-900 hover:text-white px-8 py-3 rounded uppercase font-bold tracking-widest transition-colors z-10">
              Desbloquear Cofre
           </button>
        </div>
     );
  }

  return (
    <div className="min-h-screen bg-black text-slate-300 p-8 font-mono border-t-4 border-red-600">
       <header className="flex justify-between items-center mb-10 border-b border-red-900/50 pb-4">
          <h1 className="text-red-500 font-black text-2xl tracking-[0.3em] uppercase">Dark UI Vault</h1>
          <div className="bg-red-950 text-red-500 px-4 py-2 rounded-full font-bold animate-pulse flex items-center gap-2 border border-red-800">
             <span>⏳ AUTODESTRUIÇÃO EM:</span>
             <span className="text-white">{formatTime(timeLeft)}</span>
          </div>
       </header>

       <div className="max-w-4xl mx-auto grid gap-8">
          {/* Matéria Efêmera */}
          <article className="bg-[#0a0a0c] border border-slate-800 p-6 rounded-xl hover:border-red-900 transition-colors">
             <div className="flex justify-between items-start mb-4">
                <span className="bg-red-950 text-red-500 text-[10px] font-black px-2 py-1 rounded uppercase tracking-widest">Risco Crítico</span>
                <span className="text-slate-600 text-xs">Vazado via Crawler às 03:45 AM</span>
             </div>
             <h2 className="text-2xl font-black text-white mb-4 leading-tight">
                ESCÂNDALO! Áudio vazado aponta que o Ator 'Y' estaria de malas prontas.
             </h2>
             <p className="text-slate-400 mb-6 blur-[2px] hover:blur-none transition-all cursor-pointer">
                (Passe o mouse para ler a transcrição). "Eu não aguento mais as festas dela, 
                eu vou pegar minhas malas hoje a noite e vazar daqui". A fonte indica que o advogado 
                dele já foi contatado. O nome foi ocultado pelo Juiz I.A por precaução jurídica.
             </p>
             <button className="bg-slate-900 hover:bg-red-950 text-red-500 border border-slate-700 hover:border-red-800 w-full py-4 font-black uppercase tracking-widest rounded transition-colors">
                Tocar Áudio Criptografado
             </button>
          </article>
       </div>
    </div>
  );
}
