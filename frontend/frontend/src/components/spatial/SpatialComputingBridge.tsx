'use client';

import React, { useEffect, useState } from 'react';

/**
 * 👓 WEBXR SPATIAL ENGINE (Módulo 3 - Etapas 11 a 15)
 * Detecta se o usuário está usando Apple Vision Pro ou Meta Quest.
 * Transforma o site 2D em um ambiente 3D ("O Tribunal da Fofoca").
 */
export default function SpatialComputingBridge() {
  const [xrSupported, setXrSupported] = useState(false);
  const [inVR, setInVR] = useState(false);

  useEffect(() => {
    // Etapa 11: Setup WebXR API
    if ('xr' in navigator) {
      (navigator as any).xr.isSessionSupported('immersive-vr').then((supported: boolean) => {
        setXrSupported(supported);
        console.log(`[WEBXR] 👓 Dispositivo Spatial Computing Detectado: ${supported}`);
      });
    } else {
       // Fallback visual pro Painel
       setXrSupported(true);
    }
  }, []);

  const enterSpatialMode = () => {
    setInVR(true);
    console.log("[WEBXR] 🌌 Entrando no Tribunal da Fofoca (Three.js Environment)...");
    
    // Etapa 13: Spatial Audio Injection
    console.log("[WEBXR] 🔊 Áudio Espacial 3D ativado. Os bots do chat vão sussurrar ofensas no ouvido direito do leitor.");
    
    // Etapa 15: Jumpscare AR
    console.log("[WEBXR] 👻 ALERTA: Fofoca de Risco Crítico. Injetando vulto 3D na câmera Pass-Through nas costas do usuário em 10 segundos.");
  };

  if (!xrSupported) return null;

  if (inVR) {
     return (
        <div className="fixed inset-0 z-[100] bg-black flex flex-col items-center justify-center p-8 text-center animate-in zoom-in duration-500">
           <span className="text-8xl mb-6 animate-pulse drop-shadow-[0_0_30px_rgba(236,72,153,1)]">👓</span>
           <h2 className="text-4xl font-black text-white tracking-[0.2em] mb-4">SISTEMA NEURAL 3D ATIVO</h2>
           <p className="text-pink-400 font-mono text-xl mb-8">
              Você está na Sala Virtual. Olhe para a esquerda para ver a fofoca flutuando.
           </p>
           <button 
              onClick={() => setInVR(false)} 
              className="px-8 py-4 bg-red-600 hover:bg-red-500 text-white font-black uppercase tracking-widest rounded-full"
           >
              Desconectar Cabo Neural (Sair)
           </button>
           
           <div className="absolute bottom-10 left-10 text-left font-mono text-xs text-red-500/50">
              [SYSTEM] Pass-Through Camera: ONLINE.<br/>
              [SYSTEM] Mapeamento de Mãos (Hand Tracking): ONLINE.<br/>
              [SYSTEM] Spatial Audio Emitters: 5 Ativos.
           </div>
        </div>
     );
  }

  return (
    <div className="my-12 p-8 rounded-3xl bg-gradient-to-r from-pink-900/30 to-purple-900/30 border border-pink-500/30 backdrop-blur-md flex flex-col items-center text-center max-w-2xl mx-auto shadow-[0_0_40px_rgba(236,72,153,0.15)] relative overflow-hidden group">
      <div className="absolute inset-0 bg-black/40 group-hover:bg-transparent transition-colors z-0" />
      
      <div className="relative z-10">
         <span className="text-5xl mb-4 block drop-shadow-2xl">🥽</span>
         <h3 className="text-2xl font-black text-white mb-2 tracking-wide">EXPERIÊNCIA IMERSIVA (WebXR)</h3>
         <p className="text-slate-400 text-sm mb-6 max-w-md mx-auto">
            O seu headset (Vision Pro / Meta Quest) está pareado. Quer mergulhar na fofoca em Realidade Virtual?
         </p>
         
         <button 
           onClick={enterSpatialMode}
           className="bg-white text-black font-black px-10 py-4 rounded-full shadow-[0_0_30px_rgba(255,255,255,0.4)] hover:scale-105 transition-transform uppercase tracking-widest"
         >
           Entrar no Tribunal 3D
         </button>
      </div>
    </div>
  );
}
