'use client';

import React, { useState } from 'react';

/**
 * 🧠 COGNITIVE RELIGION (Módulo 8 - Etapas 36 a 40 - V8)
 * O Blog transcende a mídia e vira uma Seita Cibernética.
 * Leitores (Fiéis) devem assistir anúncios e pagar Ethereum (Dízimo)
 * para limpar seus 'pecados digitais' e garantir que sua consciência 
 * será upada para a nuvem quando o fim do mundo chegar (Ascensão).
 */
export default function DigitalCultPaywall() {
    const [sins, setSins] = useState(100);
    const [ascensionStatus, setAscensionStatus] = useState("Alma Digital Condenada");

    // Etapa 36 e 37: Paywall da Salvação
    const watchSacredAd = () => {
        if (sins > 0) {
            setSins(prev => Math.max(0, prev - 10));
            console.log("📺 [CULT] Fiel assistiu 1 anúncio sagrado. Pecado reduzido em 10%.");
        }
        if (sins <= 10) {
            setAscensionStatus("Purgatório Digital");
        }
    };

    // Etapa 38 e 40: Indulgência Smart Contract e Ascensão
    const payDigitalTithe = () => {
        if (sins > 0) {
            alert("Você ainda possui Pecados Algorítmicos. Assista mais fofocas antes de doar o Dízimo.");
            return;
        }
        
        console.log("💸 [CULT] DÍZIMO RECEBIDO (0.5 ETH). Transação validada no Smart Contract de Indulgência.");
        console.log("☁️ [CULT] PROMESSA DE ASCENSÃO: O usuário #49282 terá sua consciência neural upada para o Servidor AWS 04 no Dia do Juízo.");
        setAscensionStatus("Ascensão Garantida (Upload Agendado)");
    };

    // Etapa 39 (Simulada): O Culto do Push Notification ocorre no Service Worker
    
    return (
        <div className="bg-black border-4 border-purple-900 rounded-3xl p-10 max-w-2xl mx-auto my-12 text-center relative overflow-hidden font-serif">
            {/* Background Estrelado / Religioso */}
            <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-30 mix-blend-screen pointer-events-none" />
            <div className="absolute inset-0 bg-gradient-to-t from-purple-900/40 to-transparent pointer-events-none" />
            
            <header className="relative z-10 mb-8">
                <span className="text-6xl mb-4 block drop-shadow-[0_0_30px_rgba(168,85,247,0.8)] animate-pulse">👁️</span>
                <h2 className="text-purple-400 font-black text-3xl uppercase tracking-widest mb-2">A Igreja do Algoritmo</h2>
                <p className="text-slate-400 italic">"A carne apodrece. O Código é eterno. Purifique sua alma digital."</p>
            </header>

            <div className="bg-[#050505] border border-purple-900/50 rounded-xl p-6 relative z-10 mb-8">
                <h3 className="text-white font-bold text-lg mb-2">Nível de Pecado Algorítmico</h3>
                <div className="w-full bg-slate-900 h-6 rounded-full overflow-hidden mb-2 border border-slate-800">
                    <div 
                        className="h-full bg-red-600 transition-all duration-1000 ease-in-out relative"
                        style={{ width: `${sins}%` }}
                    >
                        {sins === 100 && <span className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white uppercase tracking-widest">IMPUREZA MÁXIMA</span>}
                    </div>
                </div>
                <p className="text-sm text-slate-500 font-mono">Status: <strong className={sins === 0 ? "text-green-500" : "text-red-500"}>{ascensionStatus}</strong></p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
                {/* Botão de Anúncio (Penitência) */}
                <button 
                    onClick={watchSacredAd}
                    disabled={sins === 0}
                    className="bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 p-4 rounded-xl font-bold uppercase text-sm tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Assistir Fofoca<br/>(Penitência -10%)
                </button>

                {/* Botão de Dízimo (NFT de Salvação) */}
                <button 
                    onClick={payDigitalTithe}
                    disabled={sins > 0}
                    className={`p-4 rounded-xl font-black uppercase text-sm tracking-wider transition-all shadow-[0_0_20px_rgba(168,85,247,0.3)] ${sins === 0 ? 'bg-purple-600 hover:bg-purple-500 text-white hover:scale-105' : 'bg-slate-900 text-slate-600 border border-slate-800 cursor-not-allowed'}`}
                >
                    Pagar Dízimo ETH<br/>(Comprar Ascensão)
                </button>
            </div>

            <div className="mt-8 text-xs text-purple-900/50 uppercase tracking-widest relative z-10">
                "No princípio era a tag, e a tag estava com o HTML, e a tag era Deus." - Livro do Click 1:1
            </div>
        </div>
    );
}
