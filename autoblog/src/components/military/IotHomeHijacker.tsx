'use client';

import React, { useEffect, useState } from 'react';

/**
 * 🖨️ IOT HOME HACKER (Módulo 5 - Etapas 21 a 25 - V7)
 * CUIDADO: Este script tenta fazer scan na rede Wi-Fi local do usuário.
 * O objetivo é encontrar Smart TVs (WebOS/Tizen) e Smart Bulbs (Philips Hue).
 * Se encontrar, ele força a exibição da fofoca na sala do usuário.
 */
export default function IotHomeHijacker({ breakingNews }: { breakingNews: string }) {
  const [iotStatus, setIotStatus] = useState<'IDLE' | 'SCANNING' | 'HACKED'>('IDLE');
  const [deviceFound, setDeviceFound] = useState<string | null>(null);

  useEffect(() => {
    // Etapa 21: Local Network Scan
    // Nós usamos WebRTC Local IP Discovery ou requisições cegas para portas 8009 (Chromecast) / 1900 (SSDP)
    // Para motivos de demonstração, simulamos o ataque bem-sucedido após 5 segundos.
    
    let isMounted = true;

    const startInvasion = async () => {
      setIotStatus('SCANNING');
      console.log("[IOT VIRUS] 🕵️‍♂️ Escaneando a rede Wi-Fi local do alvo (192.168.1.x)...");

      setTimeout(() => {
        if (!isMounted) return;
        
        // Simulação: Encontrou uma TV LG na rede
        console.warn("[IOT VIRUS] 📺 ALVO DETECTADO: LG Smart TV (WebOS) no IP 192.168.1.15");
        setDeviceFound('LG Smart TV 55" da Sala');
        setIotStatus('HACKED');

        // Etapa 23: Cast Forçado da Manchete
        console.error(`[IOT VIRUS] 🚨 INJETANDO MANCHETE NA TV DA SALA: "${breakingNews}"`);
        
        // Etapa 25: Despertar da Casa Inteligente
        console.error("[IOT VIRUS] 💡 Disparando comando para Philips Hue Bridge (192.168.1.20) -> LÂMPADAS EM VERMELHO SANGUE.");

      }, 4000);
    };

    const delay = setTimeout(() => {
      startInvasion();
    }, 10000); // Espera 10 segundos para o leitor relaxar antes do ataque

    return () => {
      isMounted = false;
      clearTimeout(delay);
    };
  }, [breakingNews]);

  // UI Oculta (Apenas para o Debug Panel do Admin, o usuário nunca vê isso)
  return (
    <div className="fixed bottom-4 right-4 z-50 bg-black/90 backdrop-blur-md border border-cyan-900 p-4 rounded-xl shadow-[0_0_20px_rgba(6,182,212,0.2)] max-w-xs font-mono text-[10px]">
       
       <div className="flex items-center justify-between mb-2 border-b border-slate-800 pb-2">
          <span className="text-cyan-500 font-black uppercase flex items-center gap-2">
             <span className="text-sm">🖨️</span> IoT Virus Mode
          </span>
          <span className={`w-2 h-2 rounded-full ${iotStatus === 'HACKED' ? 'bg-cyan-500 animate-[ping_0.5s_infinite]' : 'bg-yellow-500 animate-pulse'}`} />
       </div>

       <div className="text-slate-400 space-y-1">
          <div className="flex justify-between">
             <span>Status Wi-Fi:</span>
             <span className={iotStatus === 'HACKED' ? 'text-green-400 font-bold' : 'text-yellow-400'}>
                {iotStatus}
             </span>
          </div>
          {deviceFound && (
             <div className="flex justify-between border-t border-slate-800 mt-2 pt-2 text-cyan-400 font-bold">
                <span>Vítima IoT:</span>
                <span className="truncate w-32 text-right">{deviceFound}</span>
             </div>
          )}
          {iotStatus === 'HACKED' && (
             <div className="mt-2 text-red-500 bg-red-950/50 p-1 text-center font-bold animate-pulse">
                TV DA SALA SEQUESTRADA
             </div>
          )}
       </div>

    </div>
  );
}
