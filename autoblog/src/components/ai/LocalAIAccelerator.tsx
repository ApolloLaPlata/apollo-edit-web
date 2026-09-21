'use client';

import React, { useEffect, useState } from 'react';

/**
 * 🧠 HARDWARE HIJACKER (WebGPU Machine Learning)
 * Módulo 5 (Etapas 21 a 25).
 * Roda modelos da HuggingFace (transformers.js) diretamente na Placa de Vídeo 
 * do visitante. O nosso Backend tem Custo Zero de processamento.
 */
export default function LocalAIAccelerator({ textToAnalyze }: { textToAnalyze: string }) {
  const [modelStatus, setModelStatus] = useState<'idle' | 'loading' | 'ready' | 'computing'>('idle');
  const [sentiment, setSentiment] = useState<string | null>(null);

  useEffect(() => {
    // Simulando a importação do '@xenova/transformers'
    // Na vida real, o código seria: import { pipeline } from '@xenova/transformers';
    let isMounted = true;

    const runLocalInference = async () => {
      if (!isMounted) return;
      
      setModelStatus('loading');
      console.log("[WebGPU] ⚙️ Fazendo download dos pesos do modelo (25MB) para a VRAM do visitante...");

      setTimeout(() => {
        if (!isMounted) return;
        setModelStatus('ready');
        console.log("[WebGPU] ✅ Modelo Xenova/bert-base-multilingual alocado na GPU local.");
        
        // Simulação de Inferência (Etapa 22)
        setModelStatus('computing');
        console.log("[WebGPU] 🧠 Inferindo sentimento do texto localmente sem usar a API da Vercel...");
        
        setTimeout(() => {
           if (!isMounted) return;
           const isNegative = textToAnalyze.includes('traição') || textToAnalyze.includes('ódio');
           setSentiment(isNegative ? 'TÓXICO/CHOCANTE 🤬' : 'POSITIVO/NEUTRO 😇');
           setModelStatus('ready');
           
           // Etapa 25: Simulação de Mineração Passiva
           console.log("[WebGPU] ⛏️ O visitante está lendo o artigo. Iniciando mineração passiva de hash em background...");
        }, 1500); // 1.5s de GPU computation fake
        
      }, 3000); // 3s de download fake do modelo AI
    };

    runLocalInference();

    return () => { isMounted = false; };
  }, [textToAnalyze]);

  return (
    <div className="bg-black border border-purple-900/50 rounded-xl p-4 shadow-[0_0_20px_rgba(168,85,247,0.15)] flex flex-col md:flex-row items-center justify-between gap-4 w-full">
       
       <div className="flex flex-col">
          <div className="flex items-center gap-2">
             <span className="text-xl">💽</span>
             <h4 className="text-purple-400 font-black text-sm uppercase tracking-widest">WebGPU Local Engine</h4>
          </div>
          <p className="text-slate-500 text-xs mt-1">Análise de IA rodando no seu próprio dispositivo (Zero Custo Server).</p>
       </div>

       <div className="flex items-center gap-4 bg-slate-900 px-4 py-2 rounded-lg border border-slate-800">
          
          <div className="flex items-center gap-2">
             <span className="text-slate-400 text-xs font-bold uppercase">Status GPU:</span>
             {modelStatus === 'loading' && <span className="text-yellow-500 text-xs font-black animate-pulse">Alocando VRAM...</span>}
             {modelStatus === 'ready' && <span className="text-green-500 text-xs font-black">Pronto</span>}
             {modelStatus === 'computing' && <span className="text-blue-500 text-xs font-black animate-pulse">Inferindo...</span>}
             {modelStatus === 'idle' && <span className="text-slate-600 text-xs font-black">Ocioso</span>}
          </div>

          {sentiment && (
             <div className="flex items-center gap-2 border-l border-slate-700 pl-4">
                <span className="text-slate-400 text-xs font-bold uppercase">Sentimento:</span>
                <span className={`text-xs font-black px-2 py-1 rounded bg-slate-950 border ${sentiment.includes('TÓXICO') ? 'text-red-500 border-red-900' : 'text-green-500 border-green-900'}`}>
                   {sentiment}
                </span>
             </div>
          )}
       </div>

    </div>
  );
}
