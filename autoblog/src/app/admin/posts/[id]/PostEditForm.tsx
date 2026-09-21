'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function PostEditForm({
  initialData,
  categories,
  socialSnippets = [],
}: {
  initialData: any;
  categories: any[];
  socialSnippets?: any[];
}) {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: initialData.title || '',
    slug: initialData.slug || '',
    coverImage: initialData.coverImage || '',
    author: initialData.author || '',
    categoryId: initialData.categoryId || '',
    isPublished: initialData.isPublished === 1 || initialData.isPublished === true,
    contentMd: initialData.contentMd || '',
  });
  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'edit' | 'split' | 'preview'>('split');
  const [customInstruction, setCustomInstruction] = useState('');
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const textStats = React.useMemo(() => {
    const text = formData.contentMd || '';
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    const readTime = Math.ceil(words / 200);
    const sentences = text.split(/[.!?]+/).filter(Boolean).length || 1;
    const syllables = Math.round(words * 1.8);
    const flesch = Math.min(100, Math.max(0, Math.round(248.83 - (1.015 * (words / sentences)) - (84.6 * (syllables / words)))));
    
    let status = '🟢 Excelente para Web';
    let color = 'text-emerald-400';
    if (flesch < 50) {
      status = '🟡 Leitura Densa';
      color = 'text-amber-400';
    } else if (flesch < 30) {
      status = '🔴 Complexo';
      color = 'text-red-400';
    }
    return { words, readTime, flesch, status, color };
  }, [formData.contentMd]);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const handleAiAction = async (instruction: string) => {
    if (!formData.contentMd) return showToast('error', 'O conteúdo do artigo está vazio.');
    setAiLoading(true);
    try {
      const res = await fetch('/api/admin/rewrite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: formData.contentMd, instruction }),
      });
      const data = await res.json();
      if (data.success) {
        setFormData((prev) => ({ ...prev, contentMd: data.result }));
        showToast('success', 'Texto refinado com sucesso pela Inteligência Artificial!');
      } else {
        showToast('error', data.error || 'Erro ao reescrever texto com a IA.');
      }
    } catch (e) {
      showToast('error', 'Falha de conexão com o servidor de IA.');
    }
    setAiLoading(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await fetch(`/api/admin/posts/${initialData.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        showToast('success', 'Artigo atualizado com sucesso no banco de dados!');
        router.refresh();
      } else {
        showToast('error', 'Erro ao atualizar o artigo no servidor.');
      }
    } catch (error) {
      console.error(error);
      showToast('error', 'Falha na requisição HTTP.');
    }
    setLoading(false);
  };

  const handleDelete = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/admin/posts/${initialData.id}`, { method: 'DELETE' });
      if (res.ok) {
        showToast('success', 'Artigo removido permanentemente com sucesso!');
        setTimeout(() => {
          router.push('/admin/posts');
          router.refresh();
        }, 1000);
      } else {
        showToast('error', 'Erro ao deletar o artigo.');
      }
    } catch (error) {
      console.error(error);
      showToast('error', 'Falha na requisição HTTP.');
    }
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 relative">
      {/* TOAST EXECUTIVO */}
      {toast && (
        <div
          className={`fixed bottom-6 right-6 z-[200] p-4 rounded-2xl border shadow-2xl flex items-center gap-3 animate-in slide-in-from-bottom-5 duration-300 ${
            toast.type === 'success'
              ? 'bg-emerald-950/90 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/90 border-red-500/50 text-red-300'
          }`}
        >
          <span className="text-lg">{toast.type === 'success' ? '✓' : '⚠️'}</span>
          <span className="text-xs font-semibold">{toast.message}</span>
          <button type="button" onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Título</label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Slug (URL)</label>
            <input
              type="text"
              required
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors font-mono text-xs"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Autor</label>
            <input
              type="text"
              value={formData.author}
              onChange={(e) => setFormData({ ...formData, author: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Categoria</label>
            <select
              value={formData.categoryId}
              onChange={(e) => setFormData({ ...formData, categoryId: e.target.value })}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="">Sem Categoria</option>
              {categories.map((cat: any) => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300">Status</label>
            <select
              value={formData.isPublished ? 'true' : 'false'}
              onChange={(e) => setFormData({ ...formData, isPublished: e.target.value === 'true' })}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="true">Publicado</option>
              <option value="false">Rascunho</option>
            </select>
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-sm font-medium text-slate-300">Imagem de Capa (URL)</label>
          <input
            type="text"
            value={formData.coverImage}
            onChange={(e) => setFormData({ ...formData, coverImage: e.target.value })}
            className="w-full bg-slate-950 border border-slate-800 rounded-md px-4 py-2 text-white focus:outline-none focus:border-cyan-500 transition-colors font-mono text-xs"
          />
          {formData.coverImage && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={formData.coverImage} alt="Cover Preview" className="mt-2 h-32 rounded object-cover border border-slate-800 shadow-md" />
          )}
        </div>

        <div className="space-y-3 pt-2">
          {/* BARRA DE TELEMETRIA EDITORIAL FLESCH-KINCAID */}
          <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/90 border border-slate-800/80 px-4 py-2.5 rounded-2xl text-xs font-mono shadow-md">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-1.5 text-slate-300">
                <span className="text-slate-500">📝 Palavras:</span>
                <span className="font-bold text-white">{textStats.words}</span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-300">
                <span className="text-slate-500">⏱️ Leitura:</span>
                <span className="font-bold text-cyan-400">~{textStats.readTime} min</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-slate-500">🧠 Legibilidade (Flesch):</span>
              <span className={`font-black text-sm ${textStats.color}`}>{textStats.flesch} PTS</span>
              <span className={`text-[10px] px-2 py-0.5 rounded-full bg-slate-950 border border-slate-800 font-bold ${textStats.color}`}>
                {textStats.status}
              </span>
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-3 border-b border-slate-800 pb-3 mt-3">
            <div>
              <label className="text-sm font-extrabold text-white flex items-center gap-2">
                <span>⚡ Editor Executivo Markdown</span>
                <span className="text-[10px] font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-800">
                  Ao Vivo
                </span>
              </label>
              <div className="flex gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800/80 mt-2">
                <button
                  type="button"
                  onClick={() => setViewMode('edit')}
                  className={`px-3 py-1 rounded text-xs font-bold transition-all ${viewMode === 'edit' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  📝 Apenas Editar
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('split')}
                  className={`px-3 py-1 rounded text-xs font-bold transition-all ${viewMode === 'split' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  ⚡ Split-Screen (Lado a Lado)
                </button>
                <button
                  type="button"
                  onClick={() => setViewMode('preview')}
                  className={`px-3 py-1 rounded text-xs font-bold transition-all ${viewMode === 'preview' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                >
                  👁️ Apenas Preview
                </button>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleAiAction('improve')}
                disabled={aiLoading}
                className="bg-purple-600/20 text-purple-300 hover:bg-purple-600/40 border border-purple-500/30 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors disabled:opacity-50"
              >
                {aiLoading ? '⏳' : '✨'} Refinar
              </button>
              <button
                type="button"
                onClick={() => handleAiAction('expand')}
                disabled={aiLoading}
                className="bg-blue-600/20 text-blue-300 hover:bg-blue-600/40 border border-blue-500/30 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors disabled:opacity-50"
              >
                {aiLoading ? '⏳' : '📈'} Expandir
              </button>
              <button
                type="button"
                onClick={() => handleAiAction('summarize')}
                disabled={aiLoading}
                className="bg-emerald-600/20 text-emerald-300 hover:bg-emerald-600/40 border border-emerald-500/30 text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1 transition-colors disabled:opacity-50"
              >
                {aiLoading ? '⏳' : '📝'} Resumir
              </button>
            </div>
          </div>

          {/* COMANDO CUSTOMIZADO PARA A IA */}
          <div className="flex gap-2 bg-slate-950 border border-slate-800 p-2 rounded-xl">
            <input
              type="text"
              placeholder="Comando Neural (Ex: reescreva em tom corporativo, adicione subtítulos ou tópicos principais)"
              value={customInstruction}
              onChange={(e) => setCustomInstruction(e.target.value)}
              className="flex-1 bg-transparent text-white px-3 py-1.5 text-xs font-medium outline-none placeholder:text-slate-500"
            />
            <button
              type="button"
              onClick={() => handleAiAction(customInstruction)}
              disabled={aiLoading || !customInstruction.trim()}
              className="bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs px-4 py-2 rounded-lg transition-colors disabled:opacity-50 shadow-md shadow-cyan-500/20"
            >
              Executar Comando
            </button>
          </div>

          <div className={`grid gap-6 mt-4 ${viewMode === 'split' ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'}`}>
            {viewMode !== 'preview' && (
              <textarea
                required
                rows={18}
                value={formData.contentMd}
                onChange={(e) => setFormData({ ...formData, contentMd: e.target.value })}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-white focus:outline-none focus:border-cyan-500 font-mono text-xs leading-relaxed custom-scrollbar shadow-inner"
                placeholder="Escreva seu artigo usando sintaxe Markdown..."
              />
            )}

            {viewMode !== 'edit' && (
              <div className="w-full bg-slate-950/90 border border-slate-800/80 rounded-xl p-6 text-slate-300 overflow-y-auto max-h-[480px] custom-scrollbar shadow-inner space-y-4 font-sans">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-[10px] font-mono uppercase tracking-wider text-slate-500">
                  <span>✨ Preview em Tempo Real (Markdown Engine)</span>
                  <span className="text-emerald-400 font-black">● LIVE RENDER</span>
                </div>
                <h1 className="text-2xl font-black text-white leading-tight">{formData.title || 'Sem Título'}</h1>
                {formData.coverImage && (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={formData.coverImage} alt="Cover" className="w-full h-48 object-cover rounded-xl border border-slate-800 shadow-lg" />
                )}
                <div className="prose prose-invert prose-sm max-w-none leading-relaxed space-y-3">
                  {formData.contentMd ? (
                    formData.contentMd.split('\n\n').map((paragraph: string, idx: number) => {
                      if (paragraph.startsWith('# ')) return <h1 key={idx} className="text-xl font-black text-white mt-4">{paragraph.replace('# ', '')}</h1>;
                      if (paragraph.startsWith('## ')) return <h2 key={idx} className="text-lg font-bold text-cyan-300 mt-3">{paragraph.replace('## ', '')}</h2>;
                      if (paragraph.startsWith('### ')) return <h3 key={idx} className="text-base font-bold text-slate-200 mt-2">{paragraph.replace('### ', '')}</h3>;
                      if (paragraph.startsWith('> ')) return <blockquote key={idx} className="border-l-4 border-cyan-500 pl-4 py-1 italic text-slate-400 bg-slate-900/50 rounded-r">{paragraph.replace('> ', '')}</blockquote>;
                      if (paragraph.startsWith('- ') || paragraph.startsWith('* ')) {
                        return (
                          <ul key={idx} className="list-disc list-inside space-y-1 text-slate-300">
                            {paragraph.split('\n').map((item: string, i: number) => <li key={i}>{item.replace(/^[-*]\s+/, '')}</li>)}
                          </ul>
                        );
                      }
                      return <p key={idx} className="text-slate-300 text-xs leading-relaxed">{paragraph}</p>;
                    })
                  ) : (
                    <p className="text-slate-600 italic text-xs">O preview do artigo renderizado aparecerá aqui em tempo real...</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI GENERATED SOCIAL MEDIA SNIPPETS (8 CANAIS + NEWSLETTER) */}
      {socialSnippets.length > 0 && (
        <div className="bg-slate-900/60 backdrop-blur-2xl border border-indigo-500/30 rounded-2xl p-6 shadow-2xl space-y-6 mt-8">
          <div>
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
              Sindicância Multi-Plataforma • 8 Redes
            </span>
            <h2 className="text-xl font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400 flex items-center gap-2 mt-1">
              <span>✨</span> Roteiros & Divulgação Gerados pela IA
            </h2>
          </div>
          <p className="text-xs text-slate-400">
            A Inteligência Neural formatou legendas, Shorts, ganchos virais e resumos VIP automaticamente para os 8 canais da sua frota.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {socialSnippets.map((snippet: any) => (
              <div key={snippet.id} className="bg-slate-950/80 border border-slate-800/80 p-4 rounded-xl relative group flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    {snippet.platform === 'instagram' ? (
                      <span className="text-pink-400 font-bold text-xs flex items-center gap-1.5">📸 Instagram Reels</span>
                    ) : snippet.platform === 'twitter' ? (
                      <span className="text-sky-400 font-bold text-xs flex items-center gap-1.5">🐦 Twitter / X</span>
                    ) : snippet.platform === 'youtube' ? (
                      <span className="text-red-400 font-bold text-xs flex items-center gap-1.5">📺 YouTube Shorts</span>
                    ) : snippet.platform === 'facebook' ? (
                      <span className="text-blue-400 font-bold text-xs flex items-center gap-1.5">👥 Facebook Feed</span>
                    ) : snippet.platform === 'tiktok' ? (
                      <span className="text-cyan-300 font-bold text-xs flex items-center gap-1.5">🎵 TikTok Track</span>
                    ) : snippet.platform === 'kwai' ? (
                      <span className="text-amber-400 font-bold text-xs flex items-center gap-1.5">⚡ Kwai Viral</span>
                    ) : snippet.platform === 'dailymotion' ? (
                      <span className="text-indigo-400 font-bold text-xs flex items-center gap-1.5">🎬 Dailymotion HD</span>
                    ) : snippet.platform === 'newsletter' ? (
                      <span className="text-orange-400 font-bold text-xs flex items-center gap-1.5">✉️ Newsletter Drop</span>
                    ) : snippet.platform === 'telegram' ? (
                      <span className="text-sky-300 font-bold text-xs flex items-center gap-1.5">✈️ Telegram VIP</span>
                    ) : snippet.platform === 'discord' ? (
                      <span className="text-indigo-300 font-bold text-xs flex items-center gap-1.5">💬 Discord Community</span>
                    ) : (
                      <span className="text-slate-400 font-bold text-xs capitalize flex items-center gap-1.5">📢 {snippet.platform}</span>
                    )}
                    <span className="text-[9px] font-mono text-slate-500">{snippet.blogName || 'Global'}</span>
                  </div>
                  <textarea
                    readOnly
                    className="w-full bg-slate-900/60 border border-slate-800/80 rounded-lg p-3 text-xs text-slate-300 font-mono resize-none h-40 focus:outline-none custom-scrollbar"
                    defaultValue={snippet.content}
                  />
                </div>
                <div className="mt-3 flex justify-end">
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(snippet.content);
                      showToast('success', `Roteiro para ${snippet.platform} copiado com sucesso!`);
                    }}
                    className="bg-indigo-600/80 hover:bg-indigo-500 text-white text-[11px] font-bold px-3 py-1.5 rounded-lg transition-all shadow-md active:scale-95 flex items-center gap-1"
                  >
                    📋 Copiar Roteiro
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-between items-center mt-8">
        <button
          type="button"
          onClick={handleDelete}
          disabled={loading}
          className="px-4 py-2 bg-red-500/10 text-red-500 border border-red-500/20 rounded hover:bg-red-500/20 transition font-medium"
        >
          Excluir Artigo
        </button>
        <div className="flex gap-4">
          <button
            type="button"
            onClick={() => router.push('/admin/posts')}
            disabled={loading}
            className="px-6 py-2 bg-slate-800 text-white rounded hover:bg-slate-700 transition font-medium"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-cyan-600 text-white rounded hover:bg-cyan-500 transition font-bold disabled:opacity-50 shadow-lg shadow-cyan-500/20"
          >
            {loading ? 'Salvando...' : 'Salvar Alterações'}
          </button>
        </div>
      </div>
    </form>
  );
}
