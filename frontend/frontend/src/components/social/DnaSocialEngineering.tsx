'use client';

import React, { useState } from 'react';

/**
 * 🧬 DNA SCRAPING & RANSOMWARE (Módulo 6 - Etapas 26 a 30)
 * O ápice da Engenharia Social.
 * Este componente se passa por um "Quiz Inocente" (Ex: Qual seu tipo sanguíneo?).
 * Nos bastidores, ele rouba o e-mail/Facebook do leitor (simulado) e usa IA 
 * para gerar uma fofoca dizendo que ALGUÉM DA FAMÍLIA DELE está sendo traído.
 * Para saber quem é, ele deve pagar um Resgate (Gossip Ransomware).
 */
export default function DnaSocialEngineering() {
  const [step, setStep] = useState<'QUIZ' | 'SCRAPING' | 'PARANOIA' | 'RANSOM'>('QUIZ');
  const [victimName, setVictimName] = useState("");

  // Etapa 26: Fake Quiz de Captação
  const handleQuizSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!victimName) return;
    
    setStep('SCRAPING');
    
    // Etapa 27: Background Web-Scraping
    console.log(`[DNA HACK] 🕵️‍♀️ Extraindo parentes de ${victimName} no Instagram/Facebook (OSINT)...`);
    
    setTimeout(() => {
       setStep('PARANOIA');
       // Etapa 28 e 29: Geração da Fofoca Pessoal & Paranoia
       console.log(`[DNA HACK] 🚨 GATILHO DE PARANOIA: Criando fofoca envolvendo o cônjuge do usuário.`);
    }, 4000);
  };

  const payRansom = () => {
    // Etapa 30: Chantagem Retida
    alert("💸 Transferindo 50 $GOSSIP da sua MetaMask... Identidade revelada: 'Era só uma brincadeira da I.A'.");
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-2xl overflow-hidden my-12 max-w-xl mx-auto shadow-2xl">
       
       {step === 'QUIZ' && (
          <div className="p-8 text-center">
             <span className="text-4xl mb-4 block">🧬</span>
             <h3 className="text-white font-black text-xl mb-2">Descubra sua Ancestralidade VIP</h3>
             <p className="text-slate-400 text-sm mb-6">Nossa I.A consegue descobrir de qual família famosa você descende. Insira seu nome completo do Facebook para o Scan Genético.</p>
             <form onSubmit={handleQuizSubmit} className="flex flex-col gap-4">
                <input 
                  type="text" 
                  value={victimName}
                  onChange={e => setVictimName(e.target.value)}
                  placeholder="Seu Nome Completo" 
                  className="bg-slate-900 border border-slate-700 p-3 rounded-lg text-white text-center focus:border-blue-500 outline-none"
                  required
                />
                <button type="submit" className="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 rounded-lg shadow-lg">
                   INICIAR SCAN GENÉTICO
                </button>
             </form>
          </div>
       )}

       {step === 'SCRAPING' && (
          <div className="p-12 text-center flex flex-col items-center">
             <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4" />
             <h3 className="text-blue-400 font-bold uppercase tracking-widest text-sm mb-2">Vasculhando Facebook/Instagram...</h3>
             <p className="text-slate-500 text-xs font-mono">Buscando certidões de casamento, marcações em fotos e ciclo social ativo.</p>
          </div>
       )}

       {step === 'PARANOIA' && (
          <div className="p-8 bg-red-950/20 border-t-4 border-red-600 animate-in fade-in zoom-in duration-500">
             <div className="flex items-center justify-center gap-3 mb-6">
                <span className="text-4xl animate-bounce">🚨</span>
                <h3 className="text-red-500 font-black text-2xl uppercase">ALERTA VERMELHO</h3>
             </div>
             
             <p className="text-white font-medium text-center text-lg mb-4">
                {victimName}, nós achamos algo. E não é sobre a sua árvore genealógica.
             </p>
             <div className="bg-black border border-red-900 p-4 rounded-lg mb-6 shadow-inner text-center text-slate-300">
                A nossa I.A cruzou os dados do seu perfil e encontrou <strong>um vazamento crítico</strong> envolvendo o seu/sua parceiro(a). Uma foto suspeita foi postada em um fórum obscuro há 2 horas atrás com um rosto conhecido.
             </div>

             <button 
               onClick={() => setStep('RANSOM')}
               className="w-full bg-red-600 hover:bg-red-500 text-white font-black uppercase py-4 rounded-xl shadow-[0_0_20px_rgba(220,38,38,0.4)] animate-pulse"
             >
               VER A FOTO VAZADA AGORA
             </button>
          </div>
       )}

       {step === 'RANSOM' && (
          <div className="p-8 bg-black text-center border-t-4 border-purple-600 animate-in slide-in-from-bottom-8">
             <span className="text-5xl mb-4 block">💸</span>
             <h3 className="text-purple-400 font-black text-xl mb-4 uppercase">Conteúdo Retido (Ransomware)</h3>
             <p className="text-slate-400 text-sm mb-6">
                Para descriptografar o nome da pessoa da sua família que foi pega no flagra e ver a foto, você precisa transferir a taxa de liberação.
             </p>
             <div className="bg-slate-900 border border-purple-900 p-4 rounded-lg mb-6">
                <span className="text-2xl font-black text-white">50 $GOSSIP</span>
                <span className="block text-xs text-slate-500 mt-1">Token On-Chain</span>
             </div>
             <button onClick={payRansom} className="bg-purple-600 hover:bg-purple-500 w-full py-3 text-white font-bold rounded-lg shadow-[0_0_15px_rgba(168,85,247,0.4)]">
                Pagar Resgate e Ver Nome
             </button>
          </div>
       )}

    </div>
  );
}
