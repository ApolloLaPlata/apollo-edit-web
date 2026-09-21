'use client';

import React, { useState } from 'react';

/**
 * 🪙 WEB3 WALLET & TOKENOMICS (Módulo 4)
 * Etapas 16 a 20: Conexão MetaMask, Smart Contract $GOSSIP, Read-to-Earn e Paywall Crypto.
 */
export default function Web3Provider({ children }: { children: React.ReactNode }) {
  const [walletAddress, setWalletAddress] = useState<string | null>(null);
  const [gossipBalance, setGossipBalance] = useState<number>(0);

  // Etapa 16: Integração MetaMask (Simulada para Front-End)
  const connectWallet = async () => {
    try {
      if (typeof window !== 'undefined' && (window as any).ethereum) {
        // Pede para o usuário conectar
        const accounts = await (window as any).ethereum.request({ method: 'eth_requestAccounts' });
        setWalletAddress(accounts[0]);
        setGossipBalance(150); // Airdrop inicial simulado
        console.log(`[WEB3] 🦊 Carteira Conectada: ${accounts[0]}`);
      } else {
        alert("Por favor, instale a extensão MetaMask no seu navegador para usar a Web3!");
      }
    } catch (err) {
      console.error("[WEB3] Conexão Rejeitada", err);
    }
  };

  // Etapa 18: Read-to-Earn (Recebe token por ler a matéria)
  const claimReadReward = () => {
    if (!walletAddress) return alert("Conecte a carteira antes de resgatar seus Fofoca Coins!");
    setGossipBalance(prev => prev + 5);
    console.log("[WEB3] 🎁 5 $GOSSIP cunhados (minted) e enviados para a carteira.");
  };

  // Etapa 20: Paywall Web3 (Gastar tokens para ler matéria +18)
  const unlockPremiumGossip = () => {
    if (gossipBalance < 50) return alert("Você precisa de 50 $GOSSIP para desbloquear essa fofoca secreta!");
    setGossipBalance(prev => prev - 50);
    alert("🔓 Transação Aprovada na Blockchain! Foto Premium Desbloqueada.");
  };

  return (
    <div className="relative">
      
      {/* 🦊 TOPBAR WEB3 */}
      <div className="bg-black border-b border-slate-800 p-4 flex justify-between items-center z-50 relative shadow-[0_0_15px_rgba(234,179,8,0.1)]">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🪙</span>
          <h1 className="text-white font-black tracking-widest uppercase text-sm">GossipChain</h1>
        </div>
        
        {walletAddress ? (
          <div className="flex items-center gap-4">
            <span className="bg-yellow-900/40 border border-yellow-500/50 text-yellow-500 px-4 py-1.5 rounded-full font-black text-sm shadow-[0_0_10px_rgba(234,179,8,0.3)]">
              {gossipBalance} $GOSSIP
            </span>
            <span className="text-slate-400 font-mono text-xs bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700">
              {walletAddress.substring(0, 6)}...{walletAddress.substring(38)}
            </span>
          </div>
        ) : (
          <button 
            onClick={connectWallet}
            className="bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-400 hover:to-yellow-400 text-black font-black px-6 py-2 rounded-full transition-all shadow-[0_0_15px_rgba(249,115,22,0.4)] flex items-center gap-2"
          >
            Conectar MetaMask 🦊
          </button>
        )}
      </div>

      {/* Conteúdo Principal (Wrapped) */}
      <div className="w-full">
         {children}

         {/* Demonstração de Ferramentas Web3 Isoladas (Debug/View) */}
         {walletAddress && (
            <div className="fixed bottom-4 right-4 bg-slate-900 border border-slate-700 p-4 rounded-xl shadow-2xl flex flex-col gap-2 z-50 max-w-sm">
               <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest text-center">Web3 Actions</h4>
               <button onClick={claimReadReward} className="bg-green-600 hover:bg-green-500 text-white font-bold py-2 rounded-lg text-sm w-full">
                 Reivindicar 5 $GOSSIP (Read-to-Earn)
               </button>
               <button onClick={unlockPremiumGossip} className="bg-purple-600 hover:bg-purple-500 text-white font-bold py-2 rounded-lg text-sm w-full">
                 Desbloquear Fofoca VIP (-50 $GOSSIP)
               </button>
            </div>
         )}
      </div>
    </div>
  );
}
