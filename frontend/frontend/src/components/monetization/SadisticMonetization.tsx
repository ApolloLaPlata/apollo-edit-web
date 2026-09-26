'use client';

import React, { useState, useEffect } from 'react';

/**
 * 💰 MOTOR DE MONETIZAÇÃO SÁDICA (Módulo 9 - Etapas 41 a 45)
 * Manipulação psicológica avançada para arrancar lucro de leitores viciados.
 * Inclui: Escassez Falsa, Injeção Dinâmica de Afiliados e Microtransações.
 */
export default function SadisticMonetization({ articleText }: { articleText: string }) {
  const [fakeTimer, setFakeTimer] = useState(59);
  const [showPopup, setShowPopup] = useState(false);
  const [detectedProduct, setDetectedProduct] = useState<string | null>(null);

  useEffect(() => {
    // Etapa 44: Escassez Falsa (Gatilho de FOMO)
    const timerInterval = setInterval(() => {
      setFakeTimer(prev => (prev > 0 ? prev - 1 : 59));
    }, 1000);

    // Pop-up Agressivo após 5 segundos
    setTimeout(() => setShowPopup(true), 5000);

    // Etapa 45: Produtos Dinâmicos (I.A lê a fofoca e vende réplicas da China)
    // Se a matéria falar de 'Prada' ou 'iPhone', cria um botão da Shopee/AliExpress
    if (articleText.toLowerCase().includes('prada')) {
        setDetectedProduct('Bolsa Prada');
    } else if (articleText.toLowerCase().includes('iphone')) {
        setDetectedProduct('iPhone 15 Pro Max');
    }

    return () => clearInterval(timerInterval);
  }, [articleText]);

  return (
    <div className="my-10 relative">
      
      {/* Etapa 45: Injeção de Link de Afiliado Contextual (Shopee/AliExpress) */}
      {detectedProduct && (
         <div className="bg-gradient-to-r from-orange-500 to-red-600 rounded-xl p-6 shadow-2xl animate-in zoom-in mb-8 flex justify-between items-center text-white">
            <div>
               <h4 className="font-black text-xl mb-1">Gostou do estilo da Fofoca?</h4>
               <p className="text-sm font-medium">Compre a Réplica Idêntica da <span className="font-black underline">{detectedProduct}</span> com 90% OFF direto da fábrica.</p>
            </div>
            <button className="bg-white text-red-600 font-black px-6 py-3 rounded-lg shadow-lg hover:scale-105 transition-transform">
               Comprar na Shopee 🛒
            </button>
         </div>
      )}

      {/* Etapa 44: Popup de Escassez Falsa (Overlays Sádicos) */}
      {showPopup && (
        <div className="fixed bottom-4 right-4 z-50 bg-black border border-yellow-500/50 p-6 rounded-xl shadow-[0_0_30px_rgba(234,179,8,0.3)] max-w-sm animate-in slide-in-from-right">
           <button onClick={() => setShowPopup(false)} className="absolute top-2 right-2 text-slate-500 hover:text-white">✕</button>
           <h3 className="text-yellow-500 font-black text-lg mb-2 flex items-center gap-2">
              <span className="text-2xl">⚠️</span> ATENÇÃO VIP
           </h3>
           <p className="text-slate-300 text-sm mb-4">
              Restam apenas <strong className="text-white text-lg">3 vagas</strong> no nosso Grupo Secreto do Telegram. O convite expira em:
           </p>
           <div className="bg-slate-900 text-red-500 font-mono text-3xl text-center py-2 rounded-lg border border-red-900 font-black">
              00:00:{fakeTimer.toString().padStart(2, '0')}
           </div>
           <button className="w-full mt-4 bg-yellow-500 hover:bg-yellow-400 text-black font-black py-3 rounded uppercase tracking-widest transition-colors">
              Garantir Vaga AGORA
           </button>
        </div>
      )}

      {/* Etapa 43: Venda de Skins pro VTuber / Avatar */}
      <div className="bg-[#1a1a24] border border-purple-900/40 p-6 rounded-xl flex items-center gap-6">
         <div className="w-16 h-16 bg-purple-900 rounded-full flex items-center justify-center text-2xl shadow-[0_0_15px_rgba(168,85,247,0.5)]">
            💅
         </div>
         <div className="flex-1">
            <h4 className="text-white font-bold mb-1">Apoie nosso Avatar (Microtransações)</h4>
            <p className="text-slate-400 text-sm mb-3">Compre uma roupa nova (Skin 3D) para a I.A usar nos próximos vídeos de fofoca!</p>
            <div className="flex gap-2">
               <button className="bg-purple-600 hover:bg-purple-500 text-white text-xs font-bold px-4 py-2 rounded border border-purple-800">
                  Vestido Gucci ($1.99)
               </button>
               <button className="bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold px-4 py-2 rounded border border-slate-700">
                  Óculos Escuros ($0.99)
               </button>
            </div>
         </div>
      </div>
      
    </div>
  );
}
