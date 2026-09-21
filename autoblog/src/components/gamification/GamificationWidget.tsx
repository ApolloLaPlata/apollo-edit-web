'use client';

import React, { useState, useEffect } from 'react';

/**
 * 🎮 Geração Z & Millenials: Motor de Gamificação
 * Adiciona Pontos de Experiência (XP) no perfil local do Leitor toda vez que ele 
 * lê um artigo ou compartilha no Zap. Transforma o ato de fofocar num jogo viciante.
 */
export default function GamificationWidget() {
  const [xp, setXp] = useState(0);
  const [level, setLevel] = useState(1);
  const [showLevelUp, setShowLevelUp] = useState(false);
  const [isClient, setIsClient] = useState(false);

  // Requisitos de XP por Level
  const levelThresholds = [0, 500, 1500, 3000, 5000, 10000];
  const ranks = ['Iniciante', 'Observador', 'Viciado', 'Paparazzi', 'Fofoqueiro Mestre', 'Deus da Fofoca'];

  useEffect(() => {
    setIsClient(true);
    const storedXp = parseInt(localStorage.getItem('reader_xp') || '0', 10);
    setXp(storedXp);
    calculateLevel(storedXp, false);

    // Listener para ganhar pontos quando outros componentes dispararem o evento 'earn_xp'
    const handleXpEvent = (e: CustomEvent) => {
      const earnedXp = e.detail || 50; // Padrão 50 XP por artigo lido
      const newXp = storedXp + earnedXp;
      setXp(newXp);
      localStorage.setItem('reader_xp', newXp.toString());
      calculateLevel(newXp, true);
    };

    window.addEventListener('earn_xp' as any, handleXpEvent);
    return () => window.removeEventListener('earn_xp' as any, handleXpEvent);
  }, []);

  const calculateLevel = (currentXp: number, notify: boolean) => {
    let newLevel = 1;
    for (let i = 0; i < levelThresholds.length; i++) {
      if (currentXp >= levelThresholds[i]) {
        newLevel = i + 1;
      }
    }
    
    // Level Up Alert!
    setLevel((prevLevel) => {
      if (prevLevel !== newLevel && notify && newLevel > 1) {
        setShowLevelUp(true);
        setTimeout(() => setShowLevelUp(false), 5000);
      }
      return newLevel;
    });
  };

  if (!isClient) return null;

  const currentMaxXp = levelThresholds[level] || levelThresholds[level - 1] * 2;
  const progressPercent = Math.min((xp / currentMaxXp) * 100, 100);

  return (
    <>
      {/* Widget Flutuante de Perfil (Fica no rodapé ou topo do layout) */}
      <div className="fixed bottom-4 right-4 md:bottom-8 md:right-8 z-40 flex flex-col items-end pointer-events-none">
        
        {/* Notificação de Level Up (Popup Explosivo) */}
        {showLevelUp && (
          <div className="mb-4 bg-gradient-to-r from-yellow-500 to-amber-500 text-white px-6 py-4 rounded-2xl shadow-[0_10px_40px_rgba(245,158,11,0.5)] flex items-center gap-4 animate-in slide-in-from-bottom-10 fade-in zoom-in duration-500">
            <span className="text-4xl animate-bounce">🏆</span>
            <div>
              <p className="text-xs uppercase font-black tracking-widest opacity-80">Parabéns!</p>
              <p className="text-lg font-bold">Você alcançou o Nível {level}</p>
            </div>
          </div>
        )}

        {/* HUD Permanente */}
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/50 p-4 rounded-2xl shadow-2xl flex items-center gap-4 pointer-events-auto cursor-pointer hover:bg-slate-800 transition-colors w-64">
          <div className="relative w-12 h-12 flex items-center justify-center bg-slate-800 rounded-full border-2 border-red-500 shrink-0">
            <span className="text-xl font-black text-white">{level}</span>
            {/* Badges de VIP Baseado no Nível */}
            {level >= 3 && (
               <span className="absolute -top-2 -right-2 text-lg drop-shadow-md">👑</span>
            )}
          </div>
          
          <div className="flex-1">
            <div className="flex justify-between items-end mb-1">
              <span className="text-xs font-bold text-slate-300 truncate max-w-[100px]">{ranks[level - 1]}</span>
              <span className="text-[10px] text-red-400 font-bold font-mono">{xp} XP</span>
            </div>
            {/* Barra de Progresso XP */}
            <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-red-600 to-red-400 rounded-full transition-all duration-1000 ease-out relative"
                style={{ width: `${progressPercent}%` }}
              >
                 <div className="absolute top-0 right-0 bottom-0 w-4 bg-white/20 blur-[2px] animate-pulse" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
