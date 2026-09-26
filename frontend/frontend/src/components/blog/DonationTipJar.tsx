'use client';
import React, { useState } from 'react';

interface DonationTipJarProps {
  pixKey?: string;
  cryptoWallet?: string;
}

export default function DonationTipJar({ pixKey, cryptoWallet }: DonationTipJarProps) {
  const [copied, setCopied] = useState<string | null>(null);

  const handleCopy = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 3000);
  };

  if (!pixKey && !cryptoWallet) return null;

  return (
    <div className="bg-gradient-to-br from-theme-surface to-slate-900 border border-theme-border/50 rounded-2xl p-8 mb-12 shadow-2xl relative overflow-hidden group">
      <div className="absolute inset-0 bg-emerald-500/5 group-hover:bg-emerald-500/10 transition-colors pointer-events-none blur-3xl"></div>
      
      <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
        <div className="w-20 h-20 bg-emerald-900/50 rounded-full flex items-center justify-center border-2 border-emerald-500/30 shrink-0 shadow-[0_0_20px_rgba(16,185,129,0.2)]">
           <span className="text-4xl">☕</span>
        </div>
        
        <div className="flex-1 text-center md:text-left">
          <h3 className="text-2xl font-black text-emerald-400 mb-2">Pague um Café para o Robô!</h3>
          <p className="text-slate-400 text-sm leading-relaxed mb-6">
            Gostou da velocidade e precisão dessa fofoca? Nossos servidores também precisam de energia! Considere enviar uma gorjeta para mantermos o ritmo de atualizações.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
            {pixKey && (
              <button 
                onClick={() => handleCopy(pixKey, 'pix')}
                className="flex items-center gap-2 px-6 py-3 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-bold rounded-xl transition-all hover:scale-105"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                {copied === 'pix' ? 'CHAVE PIX COPIADA!' : 'COPIAR PIX'}
              </button>
            )}
            
            {cryptoWallet && (
              <button 
                onClick={() => handleCopy(cryptoWallet, 'crypto')}
                className="flex items-center gap-2 px-6 py-3 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-400 font-bold rounded-xl transition-all hover:scale-105"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path></svg>
                {copied === 'crypto' ? 'CARTEIRA COPIADA!' : 'ENVIAR CRYPTO (ETH)'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
