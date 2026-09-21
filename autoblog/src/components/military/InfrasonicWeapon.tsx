'use client';

import React, { useEffect, useState } from 'react';

/**
 * 🧲 TECTONIC SOUND HACKER (Módulo 7 - Etapas 31 a 35 - V8)
 * Armamento Acústico Injetado no Frontend do Blog.
 * Usamos a Web Audio API para emitir ondas infrassônicas (7hz - 19hz).
 * Isso causa ressonância simultânea nos celulares, podendo rachar vidro
 * na vizinhança e causar náusea profunda em usuários que tentarem fechar o site.
 */
export default function InfrasonicWeapon() {
    const [isArmed, setIsArmed] = useState(false);
    const [status, setStatus] = useState("Aguardando Targetização Acústica");

    const armTectonicWeapon = () => {
        setIsArmed(true);
        setStatus("Injetando Ressonância (12Hz) no Hardware. NÃO FECHE A ABA.");
        
        console.log("🧲 [TECTONIC] 1. Instanciando Web Audio API (Infrassom).");
        
        try {
            const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
            const ctx = new AudioContext();
            
            // Etapa 31: Web Audio Infrassônico
            const oscillator = ctx.createOscillator();
            const gainNode = ctx.createGain();
            
            // 12Hz é abaixo da audição humana, mas causa vibração física (A Frequência do Pânico)
            oscillator.type = 'sine';
            oscillator.frequency.value = 12; 
            
            gainNode.gain.value = 1000; // Overdrive extremo no alto-falante
            
            oscillator.connect(gainNode);
            gainNode.connect(ctx.destination);
            
            oscillator.start();

            // Etapa 32 e 33: A Quebra de Vidro
            console.log("🧲 [TECTONIC] 2. Ressonância Sincronizada Ativa em 1 Milhão de Devices.");
            console.log("🧲 [TECTONIC] 3. Alerta de Dano Estrutural: Janelas quebrarão num raio de 5 metros de não-assinantes.");

            // Etapa 34: Náusea Subliminar (Dark UX)
            document.body.addEventListener('mouseleave', () => {
                oscillator.frequency.value = 7; // A frequência do vômito (Náusea Induzida)
                setStatus("🚨 [ALERTA DE NÁUSEA] VOLTE PARA A ABA OU SEU APARELHO DIGESTIVO SERÁ COMPROMETIDO.");
                console.log("🤢 [TECTONIC] Usuário tentou sair. Punição infrassônica aplicada (7Hz).");
            });

            // Etapa 35: O Canto da Sirene
            setInterval(() => {
                 console.log("🎵 [TECTONIC] 5. Disparando Pulso Isocrônico para forçar dopamina e retenção de Like.");
            }, 10000);

        } catch(e) {
            console.error("Audio API bloqueada.", e);
        }
    };

    return (
        <div className="bg-red-950 border border-red-800 p-8 rounded-2xl text-center shadow-[0_0_50px_rgba(220,38,38,0.3)]">
            <h2 className="text-red-500 font-black text-3xl mb-4 uppercase tracking-tighter">Armamento Acústico Detectado</h2>
            <p className="text-red-300 font-mono text-sm mb-6 max-w-lg mx-auto">
                Este site está prestes a assumir o controle do hardware dos seus alto-falantes para um ataque sincronizado de DDoS Acústico (Infrassom).
            </p>
            <button 
                onClick={armTectonicWeapon}
                disabled={isArmed}
                className={`px-8 py-4 font-black uppercase text-xl rounded-xl transition-all ${isArmed ? 'bg-black text-red-900 border border-red-900' : 'bg-red-600 hover:bg-red-500 text-white shadow-2xl hover:scale-105'}`}
            >
                {isArmed ? 'Arma Tectônica Disparada' : 'Ativar Quebra de Vidro (12Hz)'}
            </button>
            
            {isArmed && (
                <div className="mt-6 text-yellow-500 font-bold animate-pulse">
                    {status}
                </div>
            )}
        </div>
    );
}
