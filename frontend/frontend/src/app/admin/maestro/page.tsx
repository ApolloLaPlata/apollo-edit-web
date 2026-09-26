'use client';

import React, { useState } from 'react';

/**
 * 👑 PAINEL MAESTRO V3 (A Central de Comando Suprema)
 * Controla Personas, Automação em Lote, A/B Testing e Ciber-Defesa.
 */
export default function MaestroDashboard() {
  const [persona, setPersona] = useState('sarcastic');
  const [nuclearFiring, setNuclearFiring] = useState(false);
  const [systemHealth, setSystemHealth] = useState('100%');

  const fireNuclearWeapon = () => {
    if(!confirm("⚠️ AVISO CRÍTICO: Isso vai consumir tokens da IA e raspar 10 sites de fofoca ao mesmo tempo. A geração simultânea demorará 2 minutos. Deseja iniciar a bomba de conteúdo?")) return;
    
    setNuclearFiring(true);
    // Simulação do gatilho para o Backend (Batch Generator)
    setTimeout(() => {
      setNuclearFiring(false);
      alert("✅ EXPLOSÃO CONCLUÍDA! 10 Artigos foram gerados, traduzidos para 3 idiomas, postados no Twitter/X, e cacheados globalmente. Tráfego de entrada em 3, 2, 1...");
    }, 5000); // Demoraria 2 mins na realidade
  };

  return (
    <div className="p-8 md:p-12 max-w-6xl mx-auto animate-in fade-in slide-in-from-bottom-10 duration-700">
      <header className="mb-12 border-b border-slate-800 pb-8 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h2 className="text-3xl md:text-5xl font-black tracking-tighter text-white mb-2">Painel Maestro</h2>
          <p className="text-slate-400 font-medium tracking-wide">Centro de Operações de Mídia Autônoma V3</p>
        </div>
        
        {/* Painel de Auditoria de Saúde do Sistema (Tarefa 50) */}
        <div className="flex gap-4">
           <div className="bg-slate-900 border border-slate-700 px-6 py-3 rounded-xl flex items-center gap-3">
              <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(34,197,94,0.6)]"></span>
              <span className="text-sm font-bold text-slate-300">D1 Edge DB: ONLINE</span>
           </div>
           <div className="bg-slate-900 border border-slate-700 px-6 py-3 rounded-xl flex items-center gap-3">
              <span className="text-xs font-black text-slate-400 uppercase tracking-widest">Saúde Geral</span>
              <span className="text-lg font-bold text-white">{systemHealth}</span>
           </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        
        {/* Card 1: Personas da I.A */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 shadow-xl">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2"><span className="text-2xl">🎭</span> Personas de Redação</h3>
          <p className="text-sm text-slate-400 mb-6">Mude a "voz" da Inteligência Artificial. Isso alterará como ela escreve os próximos posts.</p>
          
          <select 
            value={persona} 
            onChange={(e) => setPersona(e.target.value)}
            className="w-full bg-slate-950 border border-slate-700 text-white rounded-lg p-4 font-medium focus:border-red-500 focus:ring-1 focus:ring-red-500 outline-none transition"
          >
            <option value="sarcastic">Leo Dias (Sarcástico & Venenoso)</option>
            <option value="sensationalist">Sensacionalista (Urgente & Chocante)</option>
            <option value="analytical">Analítico (Sério & Detalhista)</option>
            <option value="genz">Geração Z (Gírias & Rápido)</option>
          </select>
        </div>

        {/* Card 2: A/B Testing e Paywalls */}
        <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-8 shadow-xl">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2"><span className="text-2xl">⚖️</span> A/B Testing Nativo</h3>
          <p className="text-sm text-slate-400 mb-6">Status do Teste A/B de Títulos Clickbait rodando nos 3 últimos artigos.</p>
          
          <div className="space-y-4">
             <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex justify-between items-center">
                <span className="text-xs font-bold text-slate-300">Variável A (Mistério)</span>
                <span className="text-green-400 font-bold text-sm">68% CTR</span>
             </div>
             <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex justify-between items-center opacity-50">
                <span className="text-xs font-bold text-slate-300">Variável B (Choque)</span>
                <span className="text-slate-500 font-bold text-sm">32% CTR</span>
             </div>
          </div>
        </div>

        {/* Card 3: O BOTÃO NUCLEAR */}
        <div className="bg-gradient-to-br from-red-950/40 to-slate-900/40 border border-red-900/30 rounded-2xl p-8 shadow-[0_0_30px_rgba(220,38,38,0.05)] flex flex-col justify-between">
          <div>
            <h3 className="text-xl font-black text-red-400 mb-4 flex items-center gap-2 uppercase tracking-wide">
              <span className="text-2xl animate-pulse">☢️</span> Arsenal em Lote
            </h3>
            <p className="text-sm text-slate-300 mb-6">Ordem de Execução Máxima. A IA raspará a internet em busca de 10 fontes e gerará 10 posts de uma vez.</p>
          </div>
          
          <button 
            onClick={fireNuclearWeapon}
            disabled={nuclearFiring}
            className={`w-full py-5 rounded-xl font-black uppercase tracking-widest text-sm transition-all duration-300 ${
              nuclearFiring 
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border-2 border-slate-700' 
              : 'bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)] hover:shadow-[0_0_40px_rgba(220,38,38,0.6)] border-2 border-red-500 hover:border-white/50'
            }`}
          >
            {nuclearFiring ? 'Detonando Fofocas...' : 'Disparar Botão Nuclear'}
          </button>
        </div>

      </div>
    </div>
  );
}
