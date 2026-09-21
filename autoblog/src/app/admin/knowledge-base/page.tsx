"use client";

import React, { useState, useEffect } from 'react';

export default function KnowledgeBaseDashboard() {
  const [channelId, setChannelId] = useState('');
  const [loading, setLoading] = useState(false);
  const [content, setContent] = useState('');
  const [sourceName, setSourceName] = useState('');
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error', msg: string } | null>(null);
  const [memories, setMemories] = useState<any[]>([]);
  const [loadingMemories, setLoadingMemories] = useState(false);

  const loadMemories = async () => {
    setLoadingMemories(true);
    try {
      const res = await fetch(`/api/admin/knowledge${channelId ? `?channelId=${channelId}` : ''}`);
      const data = await res.json();
      if (data.status === 'success') {
        setMemories(data.data);
      }
    } catch(e) {}
    setLoadingMemories(false);
  };

  useEffect(() => {
    loadMemories();
  }, [channelId]);

  const handleDeleteMemory = async (id: string) => {
    if (!confirm('Deseja deletar permanentemente este conhecimento vetorial do robô?')) return;
    try {
      const res = await fetch('/api/admin/knowledge', {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      if (res.ok) loadMemories();
    } catch(e) {}
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSourceName(file.name);
      const reader = new FileReader();
      reader.onload = (event) => {
        if (event.target?.result) {
          setContent(event.target.result as string);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleIngest = async () => {
    if (!channelId || !content) {
      setFeedback({ type: 'error', msg: 'Selecione um Canal e forneça o conteúdo base.' });
      return;
    }
    
    setLoading(true);
    setFeedback(null);
    
    try {
      const res = await fetch('/api/admin/knowledge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channelId, sourceName: sourceName || 'Texto Manual', content })
      });
      
      const data = await res.json();
      if (res.ok) {
        setFeedback({ type: 'success', msg: data.message });
        setContent('');
        setSourceName('');
        loadMemories();
      } else {
        setFeedback({ type: 'error', msg: data.error || 'Erro na vetorização.' });
      }
    } catch (err: any) {
      setFeedback({ type: 'error', msg: 'Falha de comunicação com o Cérebro Vetorial.' });
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100 p-8 md:p-12 font-sans selection:bg-cyan-500/30">
      <div className="max-w-5xl mx-auto space-y-12">
        
        {/* Header Hero */}
        <div 
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-zinc-900 to-zinc-950 border border-zinc-800/50 p-10 shadow-2xl animate-fade-in-up"
        >
          <div className="absolute top-0 right-0 p-32 opacity-20 pointer-events-none">
            <div className="w-64 h-64 bg-cyan-500 rounded-full blur-[120px]" />
          </div>
          
          <div className="relative z-10 space-y-4">
            <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
              Cérebro Vetorial (RAG)
            </h1>
            <p className="text-zinc-400 max-w-2xl text-lg leading-relaxed">
              Dê identidade aos seus canais. Faça o upload dos arquivos <code className="text-cyan-400">.md</code> do Codex ou cole os manuais aqui. A Inteligência Artificial absorverá essas memórias para guiar todas as redações autônomas futuras.
            </p>
          </div>
        </div>

        {/* Ingestion Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in-up delay-100">
          {/* Controls Sidebar */}
          <div className="space-y-6 lg:col-span-1">
            <div className="bg-zinc-900/60 backdrop-blur-md rounded-2xl p-6 border border-zinc-800 shadow-xl">
              <label className="block text-sm font-semibold text-zinc-300 mb-2 uppercase tracking-wider">Identidade do Canal</label>
              <input 
                type="text" 
                placeholder="Ex: Descarga News"
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-3 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 transition-all placeholder:text-zinc-600"
              />
              
              <div className="mt-8">
                <label className="block text-sm font-semibold text-zinc-300 mb-2 uppercase tracking-wider">Upload do Codex (.md / .txt)</label>
                <div className="relative group cursor-pointer">
                  <div className="absolute -inset-1 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200" />
                  <div className="relative flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-zinc-700 rounded-xl bg-zinc-900/80 hover:bg-zinc-800 transition-colors">
                    <svg className="w-8 h-8 text-zinc-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
                    <span className="text-sm text-zinc-400 font-medium">{sourceName ? sourceName : 'Selecionar Arquivo'}</span>
                    <input type="file" accept=".txt,.md" onChange={handleFileUpload} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                  </div>
                </div>
              </div>
            </div>
            
            <button 
              onClick={handleIngest}
              disabled={loading || !content}
              className="w-full relative overflow-hidden group rounded-xl font-bold text-white shadow-[0_0_40px_-10px_rgba(6,182,212,0.4)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-cyan-600 to-blue-600 transition-all duration-300 ease-out group-hover:scale-105" />
              <div className="relative flex items-center justify-center px-6 py-4">
                {loading ? (
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                ) : (
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                )}
                {loading ? 'Sintetizando Vetores...' : 'Injetar Conhecimento'}
              </div>
            </button>

            {feedback && (
              <div className={`p-4 rounded-xl border transition-all duration-300 ${feedback.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
                <p className="text-sm font-medium">{feedback.msg}</p>
              </div>
            )}
          </div>

          {/* Text Editor */}
          <div className="lg:col-span-2">
            <div className="bg-zinc-900/60 backdrop-blur-md rounded-2xl border border-zinc-800 shadow-xl overflow-hidden h-full flex flex-col">
              <div className="bg-zinc-950/50 border-b border-zinc-800 px-6 py-4 flex justify-between items-center">
                <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center">
                  <svg className="w-4 h-4 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                  Pré-visualização do Texto (Treinamento)
                </h3>
                <span className="text-xs text-zinc-500 font-mono">{content.length} caracteres</span>
              </div>
              <textarea 
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Cole o texto de identidade do canal aqui, ou faça o upload de um arquivo ao lado. O Motor RAG vai quebrar esse texto em múltiplos parágrafos e associá-los permanentemente ao canal escolhido."
                className="w-full flex-grow bg-transparent p-6 text-zinc-300 font-mono text-sm leading-relaxed focus:outline-none resize-none placeholder:text-zinc-700"
                spellCheck="false"
              />
            </div>
          </div>
        </div>

        {/* Knowledge Base Table */}
        <div className="bg-zinc-900/60 backdrop-blur-md rounded-2xl border border-zinc-800 shadow-xl overflow-hidden mt-12 animate-fade-in-up delay-200">
          <div className="bg-zinc-950/50 border-b border-zinc-800 px-6 py-4 flex justify-between items-center">
            <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex items-center">
              <svg className="w-4 h-4 mr-2 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
              Fragmentos de Memória Absorvidos {channelId && `[${channelId}]`}
            </h3>
            <button onClick={loadMemories} className="text-zinc-400 hover:text-cyan-400 transition-colors">
              <svg className={`w-5 h-5 ${loadingMemories ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-zinc-900/80 border-b border-zinc-800 text-xs uppercase tracking-wider text-zinc-500">
                  <th className="px-6 py-4 font-medium">Fonte (Arquivo)</th>
                  <th className="px-6 py-4 font-medium">Resumo do Contexto</th>
                  <th className="px-6 py-4 font-medium text-right">Acoplado Em</th>
                  <th className="px-6 py-4 font-medium text-right">Ação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-800/50 text-sm">
                {memories.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-zinc-500">
                      Nenhuma memória encontrada. O cérebro vetorial está vazio para esta busca.
                    </td>
                  </tr>
                ) : (
                  memories.map(mem => (
                    <tr key={mem.id} className="hover:bg-zinc-800/20 transition-colors">
                      <td className="px-6 py-4 font-medium text-cyan-400">{mem.sourceName}</td>
                      <td className="px-6 py-4 text-zinc-400 font-mono text-xs max-w-md truncate" title={mem.content}>
                        {mem.content.substring(0, 100)}...
                      </td>
                      <td className="px-6 py-4 text-zinc-500 text-right whitespace-nowrap">
                        {new Date(mem.createdAt).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button 
                          onClick={() => handleDeleteMemory(mem.id)}
                          className="text-red-400/70 hover:text-red-400 p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                          title="Apagar Memória"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
}
