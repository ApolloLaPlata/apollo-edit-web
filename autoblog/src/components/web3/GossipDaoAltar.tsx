'use client';

import React, { useState } from 'react';

/**
 * ⚖️ GOSSIP DAO (A Religião DAO - Módulo 7 - Etapas 31 a 35)
 * O Blog vira uma Sociedade Secreta Descentralizada (Culto).
 * Os leitores usam seus Tokens ($GOSSIP) para VOTAR em qual celebridade 
 * a I.A deve perseguir e criar fofocas falsas no próximo mês.
 * Inclui: Sistema de "Extorsão Limpa" onde a Celebridade pode pagar pra não ser cancelada.
 */
export default function GossipDaoAltar() {
  const [votes, setVotes] = useState({ anitta: 4500, neymar: 8200, gusttavo: 1500 });
  const [userBalance, setUserBalance] = useState(150); // Simulação de saldo na MetaMask
  const [protectionPaid, setProtectionPaid] = useState(false);

  // Etapas 32 e 33: Altar da Punição & Contrato de Linchamento
  const castVote = (target: 'anitta' | 'neymar' | 'gusttavo') => {
    if (userBalance < 10) {
       alert("Você precisa de pelo menos 10 $GOSSIP para participar do Linchamento Digital.");
       return;
    }
    setUserBalance(prev => prev - 10);
    setVotes(prev => ({ ...prev, [target]: prev[target] + 10 }));
    
    console.log(`[DAO] ⚖️ Voto Computado! A Inteligência Artificial vai focar seus ataques em: ${target.toUpperCase()}`);
    
    if (votes[target] + 10 > 10000) {
       console.error(`[DAO] 🚨 ALERTA: ${target.toUpperCase()} atingiu 10.000 votos! Iniciando Geração de 50 Fofocas Destrutivas Automáticas...`);
    }
  };

  // Etapa 35: Imunidade Adquirida (Extorsão VIP)
  const payProtectionRacket = () => {
     console.log("[DAO] 💰 Pagamento de Proteção Recebido via Smart Contract (Ethereum).");
     console.log("[DAO] 🛡️ Neymar foi removido do Altar da Punição pelos próximos 30 dias.");
     setProtectionPaid(true);
  };

  return (
    <div className="bg-black border-2 border-yellow-900 rounded-3xl p-8 my-10 max-w-3xl mx-auto font-serif relative overflow-hidden">
       {/* Background Cultual */}
       <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-20 pointer-events-none" />
       
       <header className="text-center mb-10 relative z-10">
          <span className="text-5xl mb-4 block drop-shadow-[0_0_20px_rgba(234,179,8,0.5)]">⚖️</span>
          <h2 className="text-yellow-500 font-black text-3xl uppercase tracking-[0.2em] mb-2">O Altar da Punição</h2>
          <p className="text-slate-400 italic">"A voz do povo é a voz da Máquina. Escolha quem deve cair."</p>
          <div className="mt-4 bg-yellow-950/50 border border-yellow-800 text-yellow-500 text-sm font-mono py-2 px-4 rounded-full inline-flex items-center gap-2">
             Seu Poder de Voto: <strong className="text-white">{userBalance} $GOSSIP</strong>
          </div>
       </header>

       <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
          
          {/* Alvo 1 */}
          <div className="bg-[#0a0a0c] border border-slate-800 rounded-xl p-6 text-center hover:border-red-900 transition-colors flex flex-col justify-between">
             <div>
                <h4 className="text-white font-black text-lg mb-1">Anitta</h4>
                <p className="text-slate-500 text-xs mb-4">Investigação: Finanças e Treta</p>
                <div className="bg-slate-900 rounded-full h-2 mb-2 overflow-hidden border border-slate-800">
                   <div className="bg-red-600 h-full w-[45%]" />
                </div>
                <div className="text-red-500 font-mono text-sm font-bold mb-4">{votes.anitta} / 10.000</div>
             </div>
             <button onClick={() => castVote('anitta')} className="w-full bg-red-950 hover:bg-red-900 text-red-500 border border-red-900 py-2 rounded uppercase font-black text-xs tracking-widest transition-colors">
                Lichar (-10 GOSSIP)
             </button>
          </div>

          {/* Alvo 2 (O Alvo Crítico) */}
          <div className={`bg-[#0a0a0c] border rounded-xl p-6 text-center transition-colors flex flex-col justify-between ${protectionPaid ? 'border-green-900 opacity-50' : 'border-red-600 shadow-[0_0_20px_rgba(220,38,38,0.2)]'}`}>
             {protectionPaid && <div className="absolute inset-0 bg-black/60 flex items-center justify-center z-20 font-black text-green-500 uppercase tracking-widest text-xl rotate-[-15deg] backdrop-blur-sm rounded-xl border-4 border-green-900">IMUNE</div>}
             <div>
                <div className="bg-red-600 text-white text-[10px] uppercase font-black px-2 py-1 rounded mb-2 inline-block animate-pulse">ALVO MAIOR</div>
                <h4 className="text-white font-black text-lg mb-1">Neymar Jr.</h4>
                <p className="text-slate-500 text-xs mb-4">Investigação: Festas Secretas</p>
                <div className="bg-slate-900 rounded-full h-2 mb-2 overflow-hidden border border-slate-800">
                   <div className="bg-red-500 h-full w-[82%]" />
                </div>
                <div className="text-red-500 font-mono text-sm font-bold mb-4">{votes.neymar} / 10.000</div>
             </div>
             <button disabled={protectionPaid} onClick={() => castVote('neymar')} className="w-full bg-red-600 hover:bg-red-500 text-white py-2 rounded uppercase font-black text-xs tracking-widest shadow-lg">
                Lichar (-10 GOSSIP)
             </button>
          </div>

          {/* Alvo 3 */}
          <div className="bg-[#0a0a0c] border border-slate-800 rounded-xl p-6 text-center hover:border-red-900 transition-colors flex flex-col justify-between">
             <div>
                <h4 className="text-white font-black text-lg mb-1">Gusttavo Lima</h4>
                <p className="text-slate-500 text-xs mb-4">Investigação: Bens Ocultos</p>
                <div className="bg-slate-900 rounded-full h-2 mb-2 overflow-hidden border border-slate-800">
                   <div className="bg-red-600 h-full w-[15%]" />
                </div>
                <div className="text-red-500 font-mono text-sm font-bold mb-4">{votes.gusttavo} / 10.000</div>
             </div>
             <button onClick={() => castVote('gusttavo')} className="w-full bg-red-950 hover:bg-red-900 text-red-500 border border-red-900 py-2 rounded uppercase font-black text-xs tracking-widest transition-colors">
                Lichar (-10 GOSSIP)
             </button>
          </div>

       </div>

       {/* Extorsão Limpa (Para o Famoso) */}
       <div className="mt-10 border-t border-yellow-900/50 pt-6 text-center relative z-10">
          <p className="text-slate-500 text-xs mb-4">Você é um dos famosos acima? Pague a Taxa de Proteção da DAO para ser removido do Altar.</p>
          <button onClick={payProtectionRacket} className="bg-yellow-600 hover:bg-yellow-500 text-black font-black uppercase text-xs px-6 py-3 rounded-full shadow-[0_0_15px_rgba(202,138,4,0.4)] transition-all hover:scale-105">
             PAGAR 5 ETH PARA TER IMUNIDADE
          </button>
       </div>

    </div>
  );
}
