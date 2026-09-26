'use client';

import React, { useState } from 'react';

/**
 * 🪙 SISTEMA DE TOKENOMICS (Apostas de Fofoca)
 * Transforma o Blog em uma Bolsa de Valores da Fofoca.
 * O usuário usa os Pontos (XP) que ganhou lendo para apostar se 
 * a Teoria da Conspiração Gerada pela IA vai se tornar realidade!
 */
export default function TokenBetting({ postId, theoryTitle }: { postId: number, theoryTitle: string }) {
  const [tokens, setTokens] = useState(1500); // Exemplo de tokens ganhos lendo
  const [betAmount, setBetAmount] = useState(100);
  const [betPlaced, setBetPlaced] = useState<'yes' | 'no' | null>(null);

  const placeBet = (choice: 'yes' | 'no') => {
    if (betAmount > tokens) return alert("Você não tem Fofoca Coins suficientes!");
    
    setTokens(prev => prev - betAmount);
    setBetPlaced(choice);
    
    // Aqui nós mandaríamos a aposta pro banco D1 para ser resolvida depois
    console.log(`[TOKENOMICS] Aposta registrada: ${choice.toUpperCase()} no Post ${postId} - Risco de ${betAmount} FC`);
  };

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-6 mt-8 shadow-2xl relative overflow-hidden">
      
      {/* Background FX */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/4 pointer-events-none" />

      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-black text-white flex items-center gap-2">
          <span className="text-2xl">🪙</span> Fofoca Bet (Tokenomics)
        </h3>
        <div className="bg-slate-950 border border-amber-500/30 px-4 py-1 rounded-full text-amber-500 font-black text-sm flex items-center gap-2 shadow-[0_0_10px_rgba(245,158,11,0.2)]">
          Saldo: {tokens} FC
        </div>
      </div>

      <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 mb-6">
        <p className="text-slate-400 text-sm font-bold uppercase tracking-widest mb-2 text-center">A Teoria Iminente:</p>
        <p className="text-white font-medium text-center italic">"{theoryTitle}"</p>
      </div>

      {!betPlaced ? (
        <div className="flex flex-col md:flex-row items-center gap-4">
          <div className="flex-1 flex gap-2">
            <button 
              onClick={() => placeBet('yes')}
              className="flex-1 bg-green-600 hover:bg-green-500 text-white font-black py-4 rounded-xl shadow-lg border-b-4 border-green-800 hover:border-green-600 transition-all active:translate-y-1 active:border-b-0"
            >
              VAI ACONTECER (1.8x)
            </button>
            <button 
              onClick={() => placeBet('no')}
              className="flex-1 bg-red-600 hover:bg-red-500 text-white font-black py-4 rounded-xl shadow-lg border-b-4 border-red-800 hover:border-red-600 transition-all active:translate-y-1 active:border-b-0"
            >
              É FAKE NEWS (2.1x)
            </button>
          </div>
          
          <div className="w-full md:w-32">
            <label className="text-xs font-bold text-slate-500 uppercase block mb-1">Apostar (FC)</label>
            <input 
              type="number" 
              value={betAmount} 
              onChange={(e) => setBetAmount(Number(e.target.value))}
              className="w-full bg-slate-800 text-white font-bold py-3 px-4 rounded-lg border border-slate-700 outline-none focus:border-amber-500 transition-colors text-center"
            />
          </div>
        </div>
      ) : (
        <div className="bg-green-900/30 border border-green-500/50 rounded-xl p-6 text-center animate-in zoom-in">
          <h4 className="text-green-400 font-black text-lg mb-2">APOSTA REGISTRADA COM SUCESSO! 🎰</h4>
          <p className="text-slate-300 text-sm">
            Você apostou <span className="font-bold text-white">{betAmount} FC</span> que essa fofoca é <span className="font-bold text-white uppercase">{betPlaced === 'yes' ? 'Verdade' : 'Fake News'}</span>.
            Retorne amanhã para ver se a profecia se cumpriu e recolher seus lucros.
          </p>
        </div>
      )}

    </div>
  );
}
