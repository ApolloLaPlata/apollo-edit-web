'use client';

import React, { useState, useRef, useEffect } from 'react';

interface ChatMessage {
  role: 'system_bot' | 'user';
  content: string;
}

export default function ChatInterface({ blog, agentConfig }: any) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'system_bot',
      content: `Saudações, Diretor. Eu sou o Cérebro Neural Executivo do portal **${blog.name}**.\n\nMeu System Prompt atual é:\n*"${agentConfig?.personaPrompt || 'IA Editorial Padrão'}"*\n\nComo deseja calibrar minha linha editorial, tom de voz ou estratégia de SEO hoje? Dê sua ordem em linguagem natural ou selecione um comando rápido abaixo.`
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async (customMessage?: string) => {
    const userMessage = (customMessage || input).trim();
    if (!userMessage || isLoading) return;

    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    if (!customMessage) setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`/api/admin/blogs/${blog.id}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessages((prev) => [...prev, { role: 'system_bot', content: data.reply }]);
        
        // Se a IA decidiu gerar um post
        if (data.action === 'generate_post' && data.topic) {
          setMessages((prev) => [
            ...prev,
            { role: 'system_bot', content: `⚡ Iniciando redação autônoma do artigo sobre "**${data.topic}**" em background...` },
          ]);

          fetch(`/api/admin/blogs/${blog.id}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic: data.topic }),
          })
            .then((res) => res.json())
            .then((genData) => {
              if (genData.success) {
                setMessages((prev) => [
                  ...prev,
                  {
                    role: 'system_bot',
                    content: `✅ **Artigo Publicado!**\nO texto "${genData.post.title}" foi redigido pelo Lightning e já está ao vivo no portal!`,
                  },
                ]);
              } else {
                setMessages((prev) => [
                  ...prev,
                  { role: 'system_bot', content: `❌ Falha na publicação autônoma: ${genData.error}` },
                ]);
              }
            })
            .catch(() => {
              setMessages((prev) => [
                ...prev,
                { role: 'system_bot', content: `❌ Erro de conexão ao tentar finalizar o artigo.` },
              ]);
            });
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { role: 'system_bot', content: `❌ Falha ao comunicar com o Cortex IA: ${data.error || 'Erro desconhecido'}` },
        ]);
      }
    } catch (e) {
      setMessages((prev) => [...prev, { role: 'system_bot', content: '❌ Erro de rede na conexão com o servidor.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickCommands = [
    { label: '⚡ Escrever Artigo Viral Agora', cmd: `Escreva e publique imediatamente um artigo altamente viral sobre as principais tendências de ${blog.niche}.` },
    { label: '📊 Auditoria Editorial & SEO', cmd: 'Me dê um relatório editorial completo de como estamos otimizando as palavras-chave e a legibilidade dos artigos.' },
    { label: '🎭 Tom Analítico & Sóbrio', cmd: 'A partir de agora, adote uma linha editorial extremamente séria, técnica e analítica em todas as redações.' },
    { label: '🔥 Ritmo Agressivo (6 Posts/Dia)', cmd: 'Calibre seu ritmo biológico para publicar 6 artigos por dia com foco em tráfego rápido.' },
  ];

  return (
    <div className="flex-1 bg-slate-900/80 backdrop-blur-xl rounded-3xl border border-slate-800/80 flex flex-col shadow-2xl overflow-hidden min-h-[500px]">

      {/* BARRA SUPERIOR DO CHAT */}
      <div className="bg-slate-950/80 px-6 py-3.5 border-b border-slate-800 flex justify-between items-center text-xs text-slate-400 font-medium">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Canal Criptografado com o Modelo Neural do Veículo</span>
        </div>
        <div className="font-mono text-slate-500">ID: {blog.id}</div>
      </div>

      {/* ÁREA DE MENSAGENS */}
      <div ref={scrollRef} className="flex-1 p-6 overflow-y-auto space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div
              className={`max-w-[85%] md:max-w-[75%] p-5 rounded-2xl text-xs md:text-sm leading-relaxed shadow-lg ${
                msg.role === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-br-none shadow-blue-500/10'
                  : 'bg-slate-950/90 text-slate-200 border border-slate-800/80 rounded-bl-none border-l-4 border-l-blue-500'
              }`}
            >
              <div className="flex items-center justify-between gap-4 mb-2 pb-2 border-b border-white/10 text-[11px] font-bold tracking-wider uppercase">
                <span>{msg.role === 'system_bot' ? '🤖 Cortex IA Editor' : '👑 Diretor Executivo'}</span>
                <span className="text-[10px] opacity-70 font-mono font-normal">
                  {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              
              <div
                className="whitespace-pre-wrap font-normal leading-relaxed"
                dangerouslySetInnerHTML={{
                  __html: msg.content
                    .replace(/\\n/g, '<br/>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-white">$1</strong>'),
                }}
              />
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex items-start">
            <div className="bg-slate-950/90 p-5 rounded-2xl rounded-bl-none border border-slate-800 border-l-4 border-l-blue-500 text-slate-400 text-xs flex items-center gap-3">
              <div className="flex gap-1">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" />
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
              </div>
              <span className="font-semibold text-slate-300 animate-pulse">O Cortex está processando seus parâmetros neurais...</span>
            </div>
          </div>
        )}
      </div>

      {/* CHIPS DE COMANDO RÁPIDO */}
      <div className="px-6 py-2.5 bg-slate-950/60 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 shrink-0 mr-1">
          Comandos Rápidos:
        </span>
        {quickCommands.map((chip, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(chip.cmd)}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white text-[11px] font-semibold border border-slate-700/80 transition-all shrink-0 active:scale-95 disabled:opacity-50"
          >
            {chip.label}
          </button>
        ))}
      </div>

      {/* INPUT DO CHAT */}
      <div className="p-4 bg-slate-950 border-t border-slate-800">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Dê uma ordem para recalibrar o Cérebro do portal..."
            disabled={isLoading}
            className="flex-1 bg-slate-900 border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 rounded-xl px-4 py-3 text-xs md:text-sm text-white placeholder:text-slate-500 outline-none transition-all disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-40 text-white font-bold px-6 md:px-8 py-3 rounded-xl transition-all shadow-lg shadow-blue-500/20 text-xs md:text-sm shrink-0 flex items-center gap-2"
          >
            <span>ENVIAR ORDEM</span>
            <span>↗</span>
          </button>
        </div>
      </div>
    </div>
  );
}
