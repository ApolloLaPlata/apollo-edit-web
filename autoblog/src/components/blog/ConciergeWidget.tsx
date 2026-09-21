'use client';

import React, { useState, useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  recommendedAffiliate?: {
    keyword: string;
    url: string;
  };
  capturedLead?: boolean;
}

interface ConciergeWidgetProps {
  blogId?: string;
  blogName?: string;
  accentColor?: string;
}

export default function ConciergeWidget({
  blogId = 'dark-trap',
  blogName = 'Portal Executivo',
  accentColor = '#10b981'
}: ConciergeWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `Olá! Sou o **Consultor & Concierge Neural** do **${blogName}**. 🐝\n\nEstou ao vivo para tirar qualquer dúvida técnica sobre nossos artigos, recomendar equipamentos profissionais do nicho ou enviar nossos resumos VIP por e-mail. Como posso te ajudar hoje?`
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [visitorId, setVisitorId] = useState('');
  const pathname = usePathname();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Gerar ou recuperar visitorId do localStorage
    let vid = localStorage.getItem('colmeia_visitor_id');
    if (!vid) {
      vid = 'user-' + Math.random().toString(36).substring(2, 9);
      localStorage.setItem('colmeia_visitor_id', vid);
    }
    setVisitorId(vid);
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) scrollToBottom();
  }, [messages, isOpen]);

  // Extrair slug do post atual se estiver na rota /blog/[slug]
  const getPostSlug = () => {
    if (!pathname) return undefined;
    const parts = pathname.split('/');
    if (parts[1] === 'blog' && parts[2]) {
      return parts[2];
    }
    return undefined;
  };

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    const newHistory = [...messages, { role: 'user' as const, content: userMsg }];
    setMessages(newHistory);
    setLoading(true);

    try {
      const res = await fetch('/api/chat/concierge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          blogId,
          visitorId,
          postSlug: getPostSlug(),
          message: userMsg,
          history: messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
        })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        setMessages([
          ...newHistory,
          {
            role: 'assistant',
            content: data.reply,
            recommendedAffiliate: data.recommendedAffiliate,
            capturedLead: data.capturedLead
          }
        ]);
      } else {
        setMessages([
          ...newHistory,
          {
            role: 'assistant',
            content: '⚠️ Desculpe, tive uma oscilação na conexão neural. Tente novamente em alguns segundos!'
          }
        ]);
      }
    } catch (err) {
      setMessages([
        ...newHistory,
        {
          role: 'assistant',
          content: '⚠️ Erro de rede ao conectar com a central do blog.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Renderizador simples de Markdown / Links
  const renderFormattedText = (text: string) => {
    // Transformar **negrito** e [texto](url) em elementos React
    const parts = text.split(/(\[.*?\]\(.*?\))/g);
    return parts.map((part, index) => {
      const linkMatch = part.match(/\[(.*?)\]\((.*?)\)/);
      if (linkMatch) {
        return (
          <a
            key={index}
            href={linkMatch[2]}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 font-extrabold text-emerald-400 hover:text-emerald-300 underline underline-offset-2 my-1 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-500/40"
          >
            <span>👉</span>
            <span>{linkMatch[1].replace(/👉|Ver Recomendação Oficial:|Ver Oferta Recomendada:/gi, '').trim()}</span>
            <span>↗</span>
          </a>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 font-sans">
      
      {/* BOTÃO FLUTUANTE DO CONCIERGE */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="group flex items-center gap-3 bg-gradient-to-r from-slate-900 to-indigo-950 hover:from-slate-800 hover:to-indigo-900 text-white p-4 rounded-full shadow-2xl border border-indigo-500/40 transition-all duration-300 hover:scale-105 hover:shadow-indigo-500/20"
        >
          <div className="relative">
            <span className="text-2xl block animate-bounce">💬</span>
            <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-500 border-2 border-slate-900 animate-pulse" />
          </div>
          <div className="text-left pr-2 hidden sm:block">
            <div className="text-[10px] font-extrabold text-emerald-400 uppercase tracking-wider">Colmeia Neural</div>
            <div className="text-xs font-bold text-white">Fale com o Especialista AI</div>
          </div>
        </button>
      )}

      {/* JANELA DE CHAT FLUTUANTE */}
      {isOpen && (
        <div className="w-[360px] sm:w-[400px] h-[540px] bg-slate-900/95 backdrop-blur-2xl border border-slate-800 rounded-3xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-5 duration-300">
          
          {/* CABEÇALHO DO CHAT */}
          <div className="bg-gradient-to-r from-slate-900 via-indigo-950/80 to-slate-900 p-4 border-b border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-500/40 flex items-center justify-center text-xl">
                🐝
              </div>
              <div>
                <h3 className="text-xs font-extrabold text-white">{blogName}</h3>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-widest">Concierge AI • ONLINE</span>
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center text-sm font-bold transition-colors"
              title="Fechar"
            >
              ✕
            </button>
          </div>

          {/* CORPO DE MENSAGENS */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-950/40">
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'} space-y-1`}
              >
                <div className="text-[10px] font-extrabold text-slate-500 px-1">
                  {msg.role === 'user' ? 'Você' : 'Concierge AI'}
                </div>
                <div
                  className={`max-w-[88%] p-3.5 rounded-2xl text-xs leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none shadow-md font-medium'
                      : 'bg-slate-900/90 text-slate-200 border border-slate-800/80 rounded-bl-none shadow-md font-normal whitespace-pre-wrap'
                  }`}
                >
                  {renderFormattedText(msg.content)}
                </div>

                {/* BANNER DE DESTAQUE SE RECOMENDOU AFILIADO */}
                {msg.recommendedAffiliate && (
                  <div className="max-w-[88%] bg-emerald-950/90 border border-emerald-500/50 p-3 rounded-2xl rounded-bl-none shadow-lg animate-in fade-in duration-500 space-y-1.5">
                    <div className="flex items-center gap-1.5 text-[10px] font-extrabold text-emerald-400 uppercase tracking-wider">
                      <span>🛍️</span> <span>Recomendação Verificada</span>
                    </div>
                    <p className="text-[11px] text-slate-200">
                      Nossa equipe recomenda o equipamento oficial: <strong>{msg.recommendedAffiliate.keyword}</strong>.
                    </p>
                    <a
                      href={msg.recommendedAffiliate.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-center py-2 px-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black text-xs font-extrabold transition-all shadow-md"
                    >
                      👉 Ver Oferta na Loja Oficial
                    </a>
                  </div>
                )}

                {/* BANNER SE CAPTUROU LEAD */}
                {msg.capturedLead && (
                  <div className="max-w-[88%] bg-sky-950/90 border border-sky-500/50 p-2.5 rounded-2xl rounded-bl-none text-[11px] text-sky-300 font-bold flex items-center gap-2">
                    <span>🎉</span> <span>E-mail cadastrado no CRM Neural com sucesso!</span>
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-start space-y-1">
                <div className="bg-slate-900/90 border border-slate-800 p-3 rounded-2xl rounded-bl-none text-xs text-slate-400 flex items-center gap-2">
                  <span className="animate-spin text-emerald-400">⚡</span>
                  <span>Consultor analisando dados...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* BARRA DE DIGITAÇÃO */}
          <form onSubmit={handleSend} className="p-3 bg-slate-900 border-t border-slate-800 flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua dúvida ou seu e-mail VIP..."
              disabled={loading}
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 text-white font-bold text-xs p-2.5 rounded-xl transition-all shadow-md disabled:cursor-not-allowed shrink-0"
              title="Enviar mensagem"
            >
              🚀
            </button>
          </form>

          {/* RODAPÉ DO WIDGET */}
          <div className="bg-slate-950 py-1.5 px-3 text-center border-t border-slate-800/50">
            <span className="text-[9px] text-slate-500 uppercase tracking-widest font-extrabold">
              Auto-Blog CMS • Colmeia Lead Bot v2.5
            </span>
          </div>

        </div>
      )}

    </div>
  );
}
