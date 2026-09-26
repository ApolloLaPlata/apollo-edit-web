'use client';

import React, { useEffect, useRef, useState } from 'react';

/**
 * 👁️ MOTOR DE VISÃO COMPUTACIONAL (Eye-Tracking)
 * Solicita a câmera do usuário para "desbloquear conteúdo VIP" ou interagir,
 * mas nos bastidores analisa o choque facial e dilatação de pupila 
 * enquanto a pessoa lê a fofoca. (Emula API WebRTC Local)
 */
export default function EyeTracker() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [hasPermission, setHasPermission] = useState(false);
  const [shockLevel, setShockLevel] = useState(0);

  const requestCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setHasPermission(true);
        startNeuromarketingAnalysis();
      }
    } catch (err) {
      console.warn("[EYE-TRACKING] Usuário negou a câmera. Leitura Ocular Abortada.");
    }
  };

  const startNeuromarketingAnalysis = () => {
    // Simula uma I.A Facial (ex: face-api.js) rodando no Client-Side
    setInterval(() => {
      // Simula a medição da arregalada de olho do usuário (0 a 100)
      const mockShock = Math.floor(Math.random() * 100);
      setShockLevel(mockShock);

      if (mockShock > 85) {
        console.log("💥 [EYE-TRACKING] PICO DE CHOQUE DETECTADO! A fofoca explodiu a mente do usuário.");
        // O HyperAnalytics enviaria esse dado de Neuromarketing pro Banco (D1)
        // navigator.sendBeacon('/api/neuromarketing', { postId: 123, shock: mockShock })
      }
    }, 2000);
  };

  useEffect(() => {
    return () => {
      // Desliga a câmera se o componente desmontar
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="my-8 bg-slate-900 border border-slate-700/50 rounded-2xl p-6 shadow-2xl relative overflow-hidden group">
      
      {/* Background Matrix / Cyber */}
      <div className="absolute inset-0 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900 via-slate-900 to-black pointer-events-none" />

      <div className="relative z-10 flex flex-col md:flex-row items-center gap-8">
        
        {/* Frame da Câmera Escondido/Pequeno */}
        <div className="relative w-32 h-32 bg-black rounded-full overflow-hidden border-4 border-slate-800 shadow-[0_0_15px_rgba(0,0,0,0.8)] flex-shrink-0">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className="w-full h-full object-cover opacity-50 grayscale contrast-125"
          />
          {!hasPermission && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80">
              <span className="text-4xl">👁️</span>
            </div>
          )}
          
          {/* Radar Scanner FX */}
          {hasPermission && (
            <div className="absolute top-0 left-0 w-full h-1 bg-red-500/50 shadow-[0_0_10px_red] animate-[scan_2s_ease-in-out_infinite]" />
          )}
        </div>

        <div className="flex-1 text-center md:text-left">
          <h3 className="text-xl font-black text-white mb-2 uppercase tracking-wide">
            Leitura Biométrica de Choque
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Ligue sua câmera para o sistema ler a sua expressão facial enquanto lê essa notícia! Os leitores mais chocados ganham XP em dobro na plataforma.
          </p>

          {!hasPermission ? (
            <button 
              onClick={requestCamera}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors text-sm shadow-[0_0_15px_rgba(37,99,235,0.4)]"
            >
              Ativar Sensor Ocular
            </button>
          ) : (
            <div className="flex items-center gap-4 justify-center md:justify-start">
               <div className="text-xs font-bold text-slate-500 uppercase">Grau de Surpresa:</div>
               <div className="w-48 h-3 bg-slate-800 rounded-full overflow-hidden relative border border-slate-700">
                  <div 
                    className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-red-500 transition-all duration-300"
                    style={{ width: `${shockLevel}%` }}
                  />
               </div>
               <span className="text-sm font-black text-white w-8">{shockLevel}%</span>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
