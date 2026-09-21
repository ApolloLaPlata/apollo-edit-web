'use client';

import React, { useState, useRef, useEffect } from 'react';

type Message = {
  role: 'user' | 'ai';
  content: string;
};

export default function ArticleChatbot({ articleContext }: { articleContext: string }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    { role: 'ai', content: 'Olá! Sou o assistente neural deste artigo. Tem alguma dúvida sobre o texto?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const toggleChat = () => setIsOpen(!isOpen);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    const newMessages: Message[] = [...messages, { role: 'user', content: userMsg }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: newMessages, articleContext })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setMessages([...newMessages, { role: 'ai', content: data.reply }]);
      } else {
        setMessages([...newMessages, { role: 'ai', content: 'Ops, houve uma falha de conexão.' }]);
      }
    } catch (e) {
      setMessages([...newMessages, { role: 'ai', content: 'Erro ao contatar o servidor.' }]);
    }
    
    setIsLoading(false);
  };

  return (
    <>
      {/* FAB - Floating Action Button */}
      <button 
        onClick={toggleChat}
        className={`fixed bottom-6 right-6 z-50 p-4 rounded-full shadow-[0_0_20px_rgba(var(--theme-accent-rgb),0.5)] bg-theme-accent hover:bg-theme-accent-hover text-white transition-all transform hover:scale-110 flex items-center justify-center ${isOpen ? 'rotate-90 opacity-0 pointer-events-none' : 'rotate-0 opacity-100'}`}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
      </button>

      {/* Chat Window */}
      <div className={`fixed bottom-6 right-6 z-50 w-[350px] max-w-[calc(100vw-3rem)] h-[500px] max-h-[80vh] flex flex-col bg-theme-surface/90 backdrop-blur-2xl rounded-2xl shadow-2xl border border-theme-border/60 transition-all origin-bottom-right ${isOpen ? 'scale-100 opacity-100' : 'scale-50 opacity-0 pointer-events-none'}`}>
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-theme-border/60 bg-theme-bg/50 rounded-t-2xl">
          <div className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <div>
              <h3 className="font-bold text-theme-text text-sm uppercase tracking-wider">AI Copilot</h3>
              <p className="text-[10px] text-theme-muted flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span> Online
              </p>
            </div>
          </div>
          <button onClick={toggleChat} className="text-theme-muted hover:text-white transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-md ${msg.role === 'user' ? 'bg-theme-accent text-white rounded-tr-sm' : 'bg-slate-800/80 border border-slate-700 text-slate-200 rounded-tl-sm'}`}>
                {msg.content}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-slate-800/80 border border-slate-700 text-slate-200 p-3 rounded-2xl rounded-tl-sm text-sm shadow-md flex gap-1">
                <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-3 bg-theme-bg/50 border-t border-theme-border/60 rounded-b-2xl">
          <form onSubmit={sendMessage} className="flex items-center gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Pergunte sobre o texto..."
              className="flex-1 bg-slate-900/50 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-theme-accent transition-colors"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isLoading}
              className="bg-theme-accent hover:bg-theme-accent-hover disabled:opacity-50 text-white p-2 rounded-xl transition-colors shadow-lg"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
            </button>
          </form>
        </div>
      </div>
    </>
  );
}
