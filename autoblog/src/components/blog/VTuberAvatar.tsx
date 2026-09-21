'use client';

import React, { useEffect, useState } from 'react';

/**
 * 🤖 APRESENTADOR VTUBER 2.5D (Holograma de Bolso)
 * Sem usar libs pesadas, este avatar css/SVG lê as frequências de áudio 
 * da Rádio I.A ou emula movimento (Lip-Sync Simulado) para conversar com o leitor.
 */
export default function VTuberAvatar({ isSpeaking = false }: { isSpeaking?: boolean }) {
  const [mouthOpen, setMouthOpen] = useState(false);
  const [eyesClosed, setEyesClosed] = useState(false);

  useEffect(() => {
    // 1. Motor de Piscar Dinâmico (Blink Engine)
    const blinkInterval = setInterval(() => {
      setEyesClosed(true);
      setTimeout(() => setEyesClosed(false), 150); // Pisca rápido
    }, Math.random() * 4000 + 2000); // Pisca entre 2 a 6 segundos

    // 2. Motor de Lip-Sync (Sincronia Labial Falsa baseada na fala)
    let talkInterval: NodeJS.Timeout;
    if (isSpeaking) {
      talkInterval = setInterval(() => {
        setMouthOpen(prev => !prev);
      }, 120 + Math.random() * 50); // Abre e fecha a boca randomicamente simulando sibilância
    } else {
      setMouthOpen(false);
    }

    return () => {
      clearInterval(blinkInterval);
      if (talkInterval) clearInterval(talkInterval);
    };
  }, [isSpeaking]);

  return (
    <div className="relative w-48 h-48 mx-auto my-8 perspective-1000 group">
      
      {/* Círculo Holográfico de Fundo */}
      <div className={`absolute inset-0 rounded-full border-4 ${isSpeaking ? 'border-red-500 shadow-[0_0_40px_rgba(220,38,38,0.6)] animate-pulse' : 'border-slate-800'} transition-all duration-700 -z-10`} />
      <div className="absolute inset-2 bg-gradient-to-t from-slate-900 to-transparent rounded-full opacity-80" />

      {/* Avatar Container (Animação de flutuar leve) */}
      <div className={`w-full h-full relative flex flex-col items-center justify-end pb-4 transition-transform duration-1000 ${isSpeaking ? 'translate-y-1' : 'animate-[float_4s_ease-in-out_infinite]'}`}>
        
        {/* CABEÇA */}
        <div className="relative w-24 h-28 bg-slate-200 dark:bg-slate-300 rounded-[50px] shadow-inner flex flex-col items-center pt-8 border-b-4 border-slate-400">
          
          {/* Cabelo GenZ */}
          <div className="absolute -top-4 w-28 h-12 bg-red-600 rounded-t-[50px] rounded-b-xl shadow-lg" />
          <div className="absolute top-2 left-2 w-8 h-10 bg-red-500 rounded-full -rotate-12" />
          <div className="absolute top-2 right-2 w-8 h-10 bg-red-700 rounded-full rotate-12" />

          {/* OLHOS */}
          <div className="flex gap-4 z-10 w-full justify-center mt-2">
            {/* Olho Esquerdo */}
            <div className={`w-5 bg-slate-900 rounded-full transition-all duration-75 overflow-hidden flex justify-center items-center ${eyesClosed ? 'h-1 mt-2' : 'h-6'}`}>
               {!eyesClosed && <div className="w-2 h-2 bg-white rounded-full translate-x-1 -translate-y-1 opacity-80" />}
            </div>
            {/* Olho Direito */}
            <div className={`w-5 bg-slate-900 rounded-full transition-all duration-75 overflow-hidden flex justify-center items-center ${eyesClosed ? 'h-1 mt-2' : 'h-6'}`}>
               {!eyesClosed && <div className="w-2 h-2 bg-white rounded-full translate-x-1 -translate-y-1 opacity-80" />}
            </div>
          </div>

          {/* BOCA (Lip-Sync) */}
          <div className="mt-4 z-10">
            {mouthOpen ? (
              <div className="w-6 h-4 bg-slate-900 rounded-full flex justify-center items-end overflow-hidden border-2 border-slate-400">
                 {/* Língua */}
                 <div className="w-4 h-2 bg-red-500 rounded-t-full translate-y-1" />
              </div>
            ) : (
              <div className="w-4 h-1 bg-slate-800 rounded-full opacity-80" />
            )}
          </div>
        </div>

        {/* CORPO / TÓRAX */}
        <div className="w-32 h-12 bg-slate-800 rounded-t-3xl mt-[-10px] z-0 border-t-2 border-slate-600 shadow-xl flex justify-center pt-2 relative overflow-hidden">
           {/* Detalhe da Roupa Cibernética */}
           <div className="w-4 h-full bg-red-600 opacity-50 blur-sm" />
           {isSpeaking && (
              <div className="absolute top-0 left-0 w-full h-1 bg-red-400 animate-pulse" />
           )}
        </div>
      </div>

      {/* Label de Status */}
      <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-800 px-4 py-1 rounded-full text-[10px] font-black tracking-widest text-slate-400 uppercase whitespace-nowrap shadow-lg">
        {isSpeaking ? (
          <span className="text-red-500 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" /> Ao Vivo
          </span>
        ) : (
          "I.A Repórter Standby"
        )}
      </div>
    </div>
  );
}
