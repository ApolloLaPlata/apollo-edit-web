'use client';

import React, { useState, useEffect } from 'react';

/**
 * ☠️ MOTOR DE INJEÇÃO VENENOSA (Etapas 4 e 5 - V7)
 * Este componente escuta os dados biométricos (do EegBrainHijacker).
 * Se a onda cerebral do usuário indicar "TÉDIO" (Alpha > Beta), 
 * o Motor reescreve a fofoca na cara dele em tempo real, 
 * deixando o texto 10x mais agressivo para gerar um pico de dopamina e atenção.
 */
export default function PoisonInjector({ originalGossip }: { originalGossip: string }) {
  const [currentText, setCurrentText] = useState(originalGossip);
  const [boredomTimer, setBoredomTimer] = useState(0);
  const [venomLevel, setVenomLevel] = useState(0); // 0 = Normal, 1 = Veneno, 2 = Ultra Tóxico

  // Simulação: A cada 3 segundos, se o leitor não rolar a página ou se o EEG detectar tédio,
  // a I.A injeta veneno para "chocar" o leitor e forçá-lo a voltar a ler.
  useEffect(() => {
    const timer = setInterval(() => {
       setBoredomTimer(prev => prev + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (boredomTimer > 5 && venomLevel === 0) {
       console.warn("[MOTOR VENENOSO] ⚠️ Leitor Entediado (EEG Alpha Detectado). Injetando Nível 1 de Veneno...");
       setVenomLevel(1);
       setCurrentText(prev => prev + " E pasmem: fontes garantem que a briga envolveu gritos no corredor do hotel de luxo, acordando outros hóspedes!");
    }
    
    if (boredomTimer > 10 && venomLevel === 1) {
       console.error("[MOTOR VENENOSO] 🚨 TÉDIO CRÍTICO. Injetando Nível 2 de Veneno (MÁXIMO)!");
       setVenomLevel(2);
       setCurrentText(prev => prev.replace("gritos no corredor", "GRITOS, AMEAÇAS E POLÍCIA CHAMADA ÀS PRESSAS"));
    }
  }, [boredomTimer, venomLevel]);

  return (
    <div className={`p-6 rounded-2xl transition-all duration-1000 ease-in-out ${venomLevel > 0 ? 'bg-red-950/20 border border-red-900 shadow-[0_0_30px_rgba(220,38,38,0.1)]' : 'bg-transparent border border-transparent'}`}>
       
       {venomLevel > 0 && (
          <div className="flex items-center gap-2 mb-4 animate-in fade-in slide-in-from-top-4">
             <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" />
             <span className="text-red-500 text-xs font-black tracking-widest uppercase">
                Atenção Cefálica Baixa: Matéria Expandida por I.A
             </span>
          </div>
       )}

       <p className={`leading-relaxed transition-all duration-500 ${venomLevel === 2 ? 'text-red-100 text-lg font-bold' : 'text-slate-300'}`}>
          {currentText}
       </p>
    </div>
  );
}
