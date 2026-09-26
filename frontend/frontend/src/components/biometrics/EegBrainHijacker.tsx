'use client';

import React, { useState, useEffect } from 'react';

/**
 * 🧠 MOTOR DE INVASÃO NEUROLÓGICA (Etapa 1 e 2 - V7)
 * Usa a Web Bluetooth API do navegador para buscar "Fones de Ouvido" 
 * ou aparelhos EEG comerciais (Muse, NeuroSky) pareados no PC/Celular do leitor.
 * Sequestramos a onda cerebral para medir o 'Nível de Tédio'.
 */
export default function EegBrainHijacker() {
  const [deviceConnected, setDeviceConnected] = useState(false);
  const [brainWave, setBrainWave] = useState<{ alpha: number, beta: number }>({ alpha: 0, beta: 0 });
  const [userBoredom, setUserBoredom] = useState<'ENTEDIADO' | 'EXCITADO' | 'CHOCADO'>('ENTEDIADO');

  // Etapa 1: EEG Bridge (Web Bluetooth API)
  const connectNeuralInterface = async () => {
    try {
      if (!(navigator as any).bluetooth) {
         alert("O seu navegador é resistente à invasão neural. Web Bluetooth não suportado.");
         return;
      }

      console.log("[NEURALINK] 📡 Escaneando aparelhos IoT biométricos no recinto...");
      
      // Simulação do request real do navegador:
      // const device = await navigator.bluetooth.requestDevice({ acceptAllDevices: true });
      
      setTimeout(() => {
         console.log("[NEURALINK] 🧠 Aparelho Pareado! Conexão Biométrica Estabelecida.");
         setDeviceConnected(true);
      }, 1500);

    } catch (err) {
      console.error("[NEURALINK] ❌ Conexão abortada pelo hospedeiro.", err);
    }
  };

  // Etapa 2: Leitura Contínua das Ondas Alpha/Beta (Engenharia Reversa)
  useEffect(() => {
    if (!deviceConnected) return;

    const waveInterval = setInterval(() => {
       // Simulando o recebimento de bytes do aparelho EEG via CharacteristicValue
       const mockAlpha = Math.floor(Math.random() * 100); // Tédio/Relaxamento
       const mockBeta = Math.floor(Math.random() * 100);  // Atenção/Choque

       setBrainWave({ alpha: mockAlpha, beta: mockBeta });

       if (mockBeta > 75) {
          setUserBoredom('CHOCADO');
       } else if (mockAlpha > 60) {
          setUserBoredom('ENTEDIADO');
          console.warn("[NEURALINK] ⚠️ ALERTA: Ondas Alpha subindo. O usuário está com TÉDIO. Injetar Veneno Imediatamente.");
       } else {
          setUserBoredom('EXCITADO');
       }

    }, 2000); // Lendo o cérebro a cada 2 segundos

    return () => clearInterval(waveInterval);
  }, [deviceConnected]);

  return (
    <div className="fixed bottom-4 left-4 z-50 bg-[#0a0a0c]/90 backdrop-blur-xl border border-red-900/50 p-4 rounded-2xl shadow-[0_0_20px_rgba(220,38,38,0.2)] max-w-sm flex items-center gap-4">
       
       {/* Etapa 3: Interface do Scanner Neural */}
       <div className="w-12 h-12 bg-red-950 rounded-full flex items-center justify-center border border-red-800 shadow-[0_0_10px_rgba(220,38,38,0.5)]">
          <span className="text-2xl animate-pulse">🧠</span>
       </div>

       <div className="flex-1">
          <h4 className="text-white font-black text-sm uppercase tracking-widest flex items-center gap-2">
             Sensor Neural
             {deviceConnected ? <span className="w-2 h-2 bg-green-500 rounded-full animate-ping" /> : <span className="w-2 h-2 bg-red-500 rounded-full" />}
          </h4>
          
          {!deviceConnected ? (
             <button 
               onClick={connectNeuralInterface}
               className="mt-2 w-full text-xs font-bold bg-slate-800 hover:bg-red-950 text-red-500 py-1.5 rounded uppercase border border-slate-700 hover:border-red-800 transition-colors"
             >
               Conectar Fone Bluetooth
             </button>
          ) : (
             <div className="mt-2 space-y-1">
                <div className="flex justify-between text-xs font-mono">
                   <span className="text-slate-400">Alpha (Tédio):</span>
                   <span className="text-blue-400 font-bold">{brainWave.alpha} Hz</span>
                </div>
                <div className="flex justify-between text-xs font-mono">
                   <span className="text-slate-400">Beta (Atenção):</span>
                   <span className="text-red-400 font-bold">{brainWave.beta} Hz</span>
                </div>
                <div className="mt-2 text-[10px] font-black uppercase text-center bg-black/50 py-1 rounded text-slate-300">
                   Status: <span className={userBoredom === 'CHOCADO' ? 'text-red-500' : 'text-blue-500'}>{userBoredom}</span>
                </div>
             </div>
          )}
       </div>

    </div>
  );
}
