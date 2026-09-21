'use client';

import React, { useEffect, useState, useRef } from 'react';

/**
 * 💬 CHAT AO VIVO ASTROTURFING (Etapa 7, 8, 9, 10)
 * Uma sala de bate-papo falsa onde I.As se passam por leitores humanos,
 * brigando entre si para gerar raiva e retenção no leitor biológico.
 */

interface ChatMessage {
  id: string;
  author: string;
  text: string;
  role: 'human' | 'troll_ia' | 'fan_ia';
  avatarColor: string;
}

export default function LiveChatAstroturf({ postId }: { postId: number }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Rola para a mensagem mais recente automaticamente
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    // 1. Simula a Conexão com o SSE Bridge (Etapa 6)
    console.log("[LIVE CHAT] Conectado ao servidor SSE.");

    // 2. Motor Astroturf (Etapa 8, 9 e 10): Gerando avatares falsos e brigas
    let counter = 0;
    const astroturfInterval = setInterval(() => {
      counter++;
      
      let newMsg: ChatMessage;

      if (counter % 3 === 0) {
         // TROLL I.A (Etapa 9 - Acende a fogueira)
         newMsg = {
           id: Date.now().toString(),
           author: "Felipe_Sincero22",
           text: "Mentira pura. Eu sigo ela no insta e ela tava em Paris ontem. Esse site inventa muita fake news, vcs são gado de acreditar nisso.",
           role: 'troll_ia',
           avatarColor: 'bg-red-900'
         };
      } else if (counter % 2 === 0) {
         // FÃ I.A (Etapa 10 - Defende a cantora e ataca o Troll)
         newMsg = {
           id: Date.now().toString(),
           author: "AnitteiraOficial_99",
           text: "Felipe_Sincero22 cala a boca seu lixo invejoso!!! A foto saiu na revista hoje, aceita o chifre dela! Rainha nunca erra 👑👑",
           role: 'fan_ia',
           avatarColor: 'bg-pink-700'
         };
      } else {
         // I.A GENÉRICA (Leitor curioso)
         newMsg = {
           id: Date.now().toString(),
           author: "MariaAparecida1980",
           text: "Meu deus do céu... em chok!! Não acredito que ele fez isso com ela 😱",
           role: 'fan_ia',
           avatarColor: 'bg-slate-700'
         };
      }

      setMessages(prev => [...prev, newMsg]);
    }, Math.random() * 4000 + 3000); // 3 a 7 segundos de delay

    return () => clearInterval(astroturfInterval);
  }, []);

  return (
    <div className="bg-[#0f0f13] border border-slate-800 rounded-2xl flex flex-col h-[500px] shadow-2xl relative overflow-hidden my-12">
      
      {/* Cabeçalho do Chat */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-4 flex justify-between items-center z-10 shadow-md">
        <h3 className="text-white font-black flex items-center gap-2">
           <span className="w-2 h-2 bg-red-500 rounded-full animate-ping" /> Chat Ao Vivo
        </h3>
        <span className="text-xs font-bold bg-slate-800 text-slate-300 px-3 py-1 rounded-full flex items-center gap-2">
           <span className="text-green-500">●</span> 1.402 Lendo Agora
        </span>
      </div>

      {/* Área de Mensagens */}
      <div ref={scrollRef} className="flex-1 p-6 overflow-y-auto space-y-4 scroll-smooth">
        <div className="text-center text-xs font-bold text-slate-600 mb-6 uppercase tracking-widest">
          Bem-vindo ao chat da matéria
        </div>

        {messages.map((msg) => (
          <div key={msg.id} className="animate-in fade-in slide-in-from-left-4 duration-300">
             <div className="flex items-start gap-3">
                <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-xs uppercase shadow-md ${msg.avatarColor}`}>
                   {msg.author.charAt(0)}
                </div>
                <div>
                   <div className="flex items-center gap-2 mb-1">
                      <span className="text-slate-300 font-bold text-sm">{msg.author}</span>
                      {msg.role === 'troll_ia' && <span className="text-[10px] bg-red-950 text-red-500 px-2 py-0.5 rounded uppercase font-bold">Hater</span>}
                   </div>
                   <p className="text-slate-400 text-sm leading-relaxed">{msg.text}</p>
                </div>
             </div>
          </div>
        ))}
      </div>

      {/* Input de Mentira (O usuário real digita aqui) */}
      <div className="p-4 bg-slate-950 border-t border-slate-800">
         <div className="flex gap-2">
            <input 
              type="text" 
              placeholder="Fale o que você acha dessa traição..." 
              className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-red-500 transition-colors"
            />
            <button className="bg-red-600 hover:bg-red-500 text-white font-black px-6 py-3 rounded-xl transition-colors shadow-[0_0_15px_rgba(220,38,38,0.3)]">
               Enviar
            </button>
         </div>
      </div>
    </div>
  );
}
