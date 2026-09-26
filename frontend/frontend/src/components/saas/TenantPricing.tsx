'use client';

import React, { useState } from 'react';

/**
 * 💸 TELA DE PAGAMENTO SAAS (White-Label)
 * Permite que visitantes leigos comprem sua prpria cpia do Blog Autnomo
 * pagando R$ 497,00 por ms (Assinatura Stripe Recorrente).
 */
export default function TenantPricing() {
  const [loading, setLoading] = useState(false);

  const handleCheckout = () => {
    setLoading(true);
    // Simula integrao com o Stripe Checkout
    setTimeout(() => {
      alert(' Redirecionando para o Checkout do Stripe (R$ 497,00/ms)...');
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="py-24 px-6 max-w-7xl mx-auto flex flex-col items-center">
      <div className="text-center max-w-2xl mb-16 animate-in slide-in-from-bottom-10 fade-in duration-700">
        <h2 className="text-4xl md:text-5xl font-black tracking-tighter text-white mb-6">
          No apenas leia as notcias. <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-amber-500">Seja o Dono.</span>
        </h2>
        <p className="text-lg text-slate-400 font-medium">
          Transforme-se num magnata da mdia. Assine hoje e a nossa I.A construir um portal de fofocas exclusivo no seu nome, gerando notcias 24/7 sem voc escrever uma nica linha.
        </p>
      </div>

      {/* Card de Preo Premium */}
      <div className="bg-slate-900 border-2 border-red-500 rounded-3xl p-8 shadow-[0_0_50px_rgba(220,38,38,0.15)] max-w-md w-full relative animate-in zoom-in duration-700 delay-200 hover:shadow-[0_0_80px_rgba(220,38,38,0.25)] transition-shadow">
        
        <div className="absolute top-0 right-8 -translate-y-1/2 bg-red-600 text-white px-4 py-1 rounded-full text-xs font-black uppercase tracking-widest">
          SaaS V4 Pro
        </div>

        <h3 className="text-2xl font-black text-white mb-2">Rede Autnoma (White-Label)</h3>
        <p className="text-slate-400 text-sm mb-6 border-b border-slate-800 pb-6">Tudo que voc precisa para rivalizar com a mdia tradicional e lucrar no automtico.</p>
        
        <div className="mb-8">
          <span className="text-5xl font-black text-white">R$ 497</span>
          <span className="text-slate-500 font-bold ml-2">/ms</span>
        </div>

        <ul className="space-y-4 mb-8">
          <li className="flex items-center gap-3 text-slate-300 font-medium">
            <span className="text-green-500 text-xl"></span> I.A Escritora Ilimitada
          </li>
          <li className="flex items-center gap-3 text-slate-300 font-medium">
            <span className="text-green-500 text-xl"></span> Hospedagem Edge (Sem Quedas)
          </li>
          <li className="flex items-center gap-3 text-slate-300 font-medium">
            <span className="text-green-500 text-xl"></span> Gamificao de Leitores Inclusa
          </li>
          <li className="flex items-center gap-3 text-slate-300 font-medium">
            <span className="text-green-500 text-xl"></span> Subdomnio Prprio (ex: seu-nome.noticias.com)
          </li>
          <li className="flex items-center gap-3 text-slate-300 font-medium">
            <span className="text-green-500 text-xl"></span> Motor Auto-Social (Twitter/X)
          </li>
        </ul>

        <button 
          onClick={handleCheckout}
          disabled={loading}
          className="w-full bg-red-600 hover:bg-red-500 text-white font-black py-4 rounded-xl shadow-lg transition-colors flex items-center justify-center"
        >
          {loading ? 'Processando Stripe...' : 'Assinar e Criar Meu Portal'}
        </button>

        <p className="text-center text-xs text-slate-500 mt-4 font-medium">
          Cancele quando quiser. Nenhuma taxa oculta.
        </p>
      </div>
    </div>
  );
}
