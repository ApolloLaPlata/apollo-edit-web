'use client';
import React, { useState } from 'react';
import { addCategory, deleteCategory } from './actions';

export default function CategoriesClient({
  initialCategories,
  blogs,
}: {
  initialCategories: any[];
  blogs: any[];
}) {
  const [search, setSearch] = useState('');
  const [selectedBlog, setSelectedBlog] = useState('ALL');
  const [submitting, setSubmitting] = useState(false);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  const handleAdd = async (formData: FormData) => {
    setSubmitting(true);
    try {
      await addCategory(formData);
      showToast('success', 'Nova categoria cadastrada com sucesso na rede!');
    } catch (e: any) {
      showToast('error', 'Falha ao salvar categoria.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    try {
      await deleteCategory(id);
      showToast('success', `Categoria "${name}" removida com sucesso!`);
    } catch (e: any) {
      showToast('error', 'Falha ao excluir categoria.');
    }
  };

  const filteredCategories = initialCategories.filter((cat) => {
    const matchesSearch =
      cat.name.toLowerCase().includes(search.toLowerCase()) ||
      cat.slug?.toLowerCase().includes(search.toLowerCase()) ||
      cat.blogName?.toLowerCase().includes(search.toLowerCase());
    const matchesBlog = selectedBlog === 'ALL' || cat.blogId === selectedBlog;
    return matchesSearch && matchesBlog;
  });

  const totalPostsInCategories = initialCategories.reduce((acc, c) => acc + (c.postCount || 0), 0);

  return (
    <div className="space-y-10 relative">
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
          <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white ml-2 text-xs font-bold">
            ✕
          </button>
        </div>
      )}

      {/* HEADER CORPORATIVO */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-cyan-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              TAXONOMIA & NICHOS ENTERPRISE
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Gestão de Categorias & Nichos
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Estruture a hierarquia editorial de todos os seus portais. O Enxame Criador e o Oráculo utilizam estes nichos para segmentar e direcionar a redação autônoma.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Categorias</span>
              <span className="text-2xl font-extrabold text-white font-mono">{initialCategories.length}</span>
            </div>
            <div className="text-center px-3 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Portais</span>
              <span className="text-2xl font-extrabold text-cyan-400 font-mono">{blogs.length}</span>
            </div>
            <div className="text-center px-3">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Artigos</span>
              <span className="text-2xl font-extrabold text-blue-400 font-mono">{totalPostsInCategories}</span>
            </div>
          </div>
        </div>
      </div>

      {/* GRID DE LAYOUT: FORMULÁRIO + TABELA */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* FORMULÁRIO DE NOVA CATEGORIA */}
        <div className="bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-slate-800/80 p-8 shadow-2xl space-y-6">
          <div className="border-b border-slate-800/80 pb-4">
            <span className="text-[10px] font-black uppercase tracking-widest text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded-md border border-cyan-500/20">
              Novo Nicho
            </span>
            <h2 className="text-xl font-bold text-white mt-2 flex items-center gap-2">
              <span>➕</span> Cadastrar Categoria
            </h2>
          </div>

          <form action={handleAdd} className="space-y-5">
            <div>
              <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider mb-2">
                Nome do Nicho / Categoria
              </label>
              <input
                type="text"
                name="name"
                required
                placeholder="Ex: Finanças e Negócios, Inteligência Artificial..."
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-extrabold text-slate-300 uppercase tracking-wider mb-2">
                Portal de Destino
              </label>
              <select
                name="blogId"
                required
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-white text-sm font-bold focus:outline-none focus:border-cyan-500 transition-colors cursor-pointer"
              >
                {blogs.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name} ({b.domain})
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={submitting || blogs.length === 0}
              className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white font-black py-3.5 rounded-xl shadow-lg shadow-cyan-500/20 transition-all text-xs uppercase tracking-wider flex items-center justify-center gap-2 active:scale-95 mt-2"
            >
              {submitting ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Salvando Nicho...
                </>
              ) : (
                <>
                  <span>✓</span> Cadastrar Categoria
                </>
              )}
            </button>
          </form>
        </div>

        {/* TABELA DE CATEGORIAS EXISTENTES */}
        <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-2xl rounded-3xl border border-slate-800/80 p-8 shadow-2xl space-y-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800/80 pb-6">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <span>🗂️</span> Taxonomia da Frota
              </h2>
              <span className="text-xs text-slate-400 font-mono">Exibindo {filteredCategories.length} categorias</span>
            </div>

            <div className="flex gap-2 w-full sm:w-auto">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Filtrar por nome..."
                className="bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors w-full sm:w-48"
              />
              <select
                value={selectedBlog}
                onChange={(e) => setSelectedBlog(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 font-bold focus:outline-none focus:border-cyan-500 cursor-pointer"
              >
                <option value="ALL">Todos Portais</option>
                {blogs.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {filteredCategories.length === 0 ? (
            <div className="py-16 text-center text-slate-500 font-medium">
              <span className="text-4xl block mb-3 opacity-30">📂</span>
              Nenhuma categoria encontrada para este filtro.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-slate-800/80 text-[10px] uppercase tracking-widest text-slate-500 bg-slate-950/40">
                    <th className="p-4 font-bold">Categoria / Nicho</th>
                    <th className="p-4 font-bold">URL Slug</th>
                    <th className="p-4 font-bold">Portal Vinculado</th>
                    <th className="p-4 font-bold">Artigos</th>
                    <th className="p-4 font-bold text-right">Ação</th>
                  </tr>
                </thead>
                <tbody className="text-sm divide-y divide-slate-800/50">
                  {filteredCategories.map((cat) => (
                    <tr key={cat.id} className="hover:bg-slate-800/40 transition-colors group">
                      <td className="p-4 font-bold text-white group-hover:text-cyan-400 transition-colors">
                        {cat.name}
                      </td>
                      <td className="p-4 font-mono text-xs text-slate-500">/{cat.slug}</td>
                      <td className="p-4">
                        <span className="bg-slate-950/80 px-2.5 py-1 rounded-md text-[10px] font-extrabold uppercase tracking-wider text-cyan-300 border border-cyan-900/50">
                          {cat.blogName || 'Geral'}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {cat.postCount || 0} matérias
                        </span>
                      </td>
                      <td className="p-4 text-right">
                        <button
                          onClick={() => handleDelete(cat.id, cat.name)}
                          className="bg-red-500/10 hover:bg-red-600 text-red-400 hover:text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-all border border-red-500/20 hover:border-red-500 shadow-sm active:scale-95"
                        >
                          Excluir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
