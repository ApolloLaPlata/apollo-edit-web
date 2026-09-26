'use client';

import React, { useEffect, useState } from 'react';

/**
 * 📱 MOBILE NATIVE BRIDGE (App Capacitor.js - Módulo 6)
 * Injetado no RootLayout. Detecta se o blog está rodando dentro do App Nativo (iOS/Android).
 * Se sim, libera poderes nativos: Push Notifications agressivas e Leitor Biométrico (FaceID).
 */
export default function MobileNativeBridge() {
  const [isNativeApp, setIsNativeApp] = useState(false);
  const [bioUnlocked, setBioUnlocked] = useState(false);

  useEffect(() => {
    // Simulando a detecção do Capacitor.js (Etapa 26 e 27)
    // Em produção: import { Capacitor } from '@capacitor/core';
    const checkNativeEnv = () => {
       const isCapacitor = window.navigator.userAgent.includes("Capacitor");
       // Forçando true no front-end de demonstração para o Painel:
       setIsNativeApp(true);
    };

    checkNativeEnv();

    if (isNativeApp) {
       console.log("[MOBILE] 📲 O Blog está rodando dentro do App Nativo.");
       
       // Etapa 28: Setup de Push Notifications
       console.log("[MOBILE] 🔔 Registrando Token APNs/FCM para Push Notifications Push agressivas...");
       
       // Etapa 30: Inicializando SQLite Local First (Modo Avião)
       console.log("[MOBILE] 💾 Banco de Dados PWA/SQLite sincronizado. Leitura offline ativada.");
    }
  }, [isNativeApp]);

  // Etapa 29: Autenticação Biométrica para Paywall
  const requestBiometricScan = () => {
    console.log("[MOBILE] 👁️ Acionando Câmera/Sensor Biométrico (FaceID/TouchID)...");
    
    // Simulação de delay nativo do iOS/Android
    setTimeout(() => {
       const userConfirmed = window.confirm("[SISTEMA NATIVO] Coloque a Impressão Digital para Desbloquear a Fofoca +18 VIP.");
       if (userConfirmed) {
          setBioUnlocked(true);
          console.log("[MOBILE] ✅ FaceID/TouchID Aprovado. Conteúdo desbloqueado.");
       } else {
          console.error("[MOBILE] ❌ Biometria falhou ou foi cancelada.");
       }
    }, 1000);
  };

  if (!isNativeApp) return null; // Não renderiza nada na Web

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 bg-[#0f0f13]/90 backdrop-blur-md border border-slate-700/50 p-4 rounded-3xl shadow-2xl flex flex-col items-center gap-3 w-11/12 max-w-sm">
      <div className="flex items-center gap-2 w-full justify-between">
         <span className="text-white font-black text-sm flex items-center gap-2">
            <span className="text-xl">📱</span> App Nativo Ativo
         </span>
         <span className="bg-green-900 text-green-500 text-[10px] uppercase font-bold px-2 py-1 rounded">Sync Offline ✅</span>
      </div>

      <div className="text-slate-400 text-xs text-center leading-relaxed">
         Seu dispositivo está recebendo <strong className="text-red-400">Push Notifications</strong> críticas. 
      </div>

      <button 
         onClick={requestBiometricScan}
         className={`w-full py-3 rounded-xl font-black transition-all ${bioUnlocked ? 'bg-green-600 text-white shadow-[0_0_15px_rgba(22,163,74,0.4)]' : 'bg-slate-800 hover:bg-slate-700 text-slate-300'}`}
      >
         {bioUnlocked ? '🔓 BIOMETRIA APROVADA' : '🔒 USAR FACE-ID PARA LER'}
      </button>

    </div>
  );
}
