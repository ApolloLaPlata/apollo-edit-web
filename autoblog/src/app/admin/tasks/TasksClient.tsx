'use client';
import React, { useState, useEffect } from 'react';

const COLUMNS_CONFIG = {
  ideias: { id: 'ideias', title: '💡 Fila da IA (Backlog)', color: 'border-amber-500/30 text-amber-400 bg-amber-500/10' },
  rascunho: { id: 'rascunho', title: '✍️ IA Redigindo', color: 'border-blue-500/30 text-blue-400 bg-blue-500/10' },
  revisao: { id: 'revisao', title: '🔍 Falha ou Revisão', color: 'border-red-500/30 text-red-400 bg-red-500/10' },
  publicado: { id: 'publicado', title: '✅ Publicado na Frota', color: 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10' },
};

interface KanbanTask {
  id: string;
  title: string;
  assigne: string;
  columnId: string;
}

export default function TasksClient() {
  const [tasks, setTasks] = useState<KanbanTask[]>([]);
  const [draggedTask, setDraggedTask] = useState<KanbanTask | null>(null);
  const [loading, setLoading] = useState(true);
  const [newTitle, setNewTitle] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Toast State
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 5000);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      const res = await fetch('/api/admin/tasks');
      const json = await res.json();
      if (json.success) {
        setTasks(json.tasks || []);
      }
    } catch (e) {
      showToast('error', 'Falha ao carregar fila de redação.');
    } finally {
      setLoading(false);
    }
  };

  const createNewTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;

    setSubmitting(true);
    try {
      const res = await fetch('/api/admin/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle.trim(),
          assigne: 'Enxame IA',
          columnId: 'ideias',
        }),
      });
      const json = await res.json();
      if (json.success && json.task) {
        setTasks((prev) => [json.task, ...prev]);
        setNewTitle('');
        showToast('success', 'Pauta injetada com sucesso na Fila da IA!');
      } else {
        showToast('error', 'Erro ao injetar pauta na fila.');
      }
    } catch (e) {
      showToast('error', 'Falha de conexão com o servidor neural.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string, title: string) => {
    setTasks((prev) => prev.filter((t) => t.id !== id));
    try {
      await fetch(`/api/admin/tasks?id=${id}`, { method: 'DELETE' });
      showToast('success', `Pauta "${title.slice(0, 25)}..." removida da fila!`);
    } catch (e) {
      showToast('error', 'Erro ao excluir pauta.');
      fetchTasks();
    }
  };

  const handleDragStart = (e: React.DragEvent, task: KanbanTask) => {
    setDraggedTask(task);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', task.id);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, targetColId: string) => {
    e.preventDefault();
    if (!draggedTask) return;
    if (draggedTask.columnId === targetColId) return;

    // Atualização otimista
    setTasks((prev) =>
      prev.map((t) => (t.id === draggedTask.id ? { ...t, columnId: targetColId } : t))
    );

    try {
      await fetch('/api/admin/tasks', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: draggedTask.id, columnId: targetColId }),
      });
      showToast('success', `Status da pauta atualizado para "${COLUMNS_CONFIG[targetColId as keyof typeof COLUMNS_CONFIG].title}"!`);
    } catch (e) {
      showToast('error', 'Erro ao sincronizar nova posição no SQLite.');
      fetchTasks();
    }

    setDraggedTask(null);
  };

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 font-medium text-sm tracking-wide animate-pulse">
          Carregando Centro de Comando Kanban (Redação IA)...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8 relative">
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
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-gradient-to-bl from-indigo-500/10 via-blue-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-40 -mt-40" />

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold tracking-wide">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
              FLUXO NEURAL KANBAN
            </div>
            <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
              Fila de Redação & Cérebro IA
            </h1>
            <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
              Quadro de controle de pautas em tempo real. O Enxame Criador recolhe automaticamente matérias na coluna <strong className="text-amber-400 font-semibold">"Fila da IA"</strong> e processa a redação e publicação.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4 bg-slate-950/60 p-5 rounded-2xl border border-slate-800/80 backdrop-blur-md shadow-inner">
            <div className="text-center px-4 border-r border-slate-800/80">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Em Fila / Backlog</span>
              <span className="text-2xl font-extrabold text-amber-400 font-mono">
                {tasks.filter((t) => t.columnId === 'ideias').length}
              </span>
            </div>
            <div className="text-center px-4">
              <span className="text-[10px] font-bold uppercase text-slate-500 block">Total Publicados</span>
              <span className="text-2xl font-extrabold text-emerald-400 font-mono">
                {tasks.filter((t) => t.columnId === 'publicado').length}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* BARRA DE INJEÇÃO RÁPIDA DE PAUTA (SEM PROMPT DIALOG!) */}
      <form
        onSubmit={createNewTask}
        className="bg-slate-900/60 backdrop-blur-md p-4 rounded-2xl border border-slate-800/80 flex flex-col sm:flex-row items-center gap-3 shadow-xl"
      >
        <div className="relative flex-1 w-full">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
            💡
          </span>
          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Injetar pauta manual para o Enxame IA redigir (ex: 5 Estratégias de Investimento em 2026)..."
            className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            disabled={submitting}
          />
        </div>
        <button
          type="submit"
          disabled={submitting || !newTitle.trim()}
          className="w-full sm:w-auto bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-extrabold text-xs uppercase tracking-wider transition-all shadow-lg shadow-indigo-500/20 active:scale-95 whitespace-nowrap flex items-center justify-center gap-2"
        >
          {submitting ? (
            <>
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Injetando...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Injetar na Fila</span>
            </>
          )}
        </button>
      </form>

      {/* QUADRO KANBAN RESPONSIVO */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 items-start">
        {Object.values(COLUMNS_CONFIG).map((col) => {
          const colTasks = tasks.filter((t) => t.columnId === col.id);
          return (
            <div
              key={col.id}
              className="bg-slate-900/60 backdrop-blur-2xl border border-slate-800/80 rounded-3xl flex flex-col shadow-2xl overflow-hidden min-h-[450px]"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, col.id)}
            >
              {/* CABEÇALHO DA COLUNA */}
              <div className="p-5 border-b border-slate-800/80 bg-slate-950/40 flex justify-between items-center">
                <span className="font-extrabold text-sm text-white">{col.title}</span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${col.color}`}>
                  {colTasks.length}
                </span>
              </div>

              {/* LISTA DE CARDS */}
              <div className="p-4 flex-1 overflow-y-auto space-y-3.5 custom-scrollbar max-h-[600px]">
                {colTasks.length === 0 ? (
                  <div className="h-48 flex flex-col items-center justify-center text-center text-slate-600 font-medium border-2 border-dashed border-slate-800/60 rounded-2xl p-4">
                    <span className="text-2xl mb-2 opacity-30">📂</span>
                    <span className="text-xs">Arraste pautas para cá</span>
                  </div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, task)}
                      className="bg-slate-950/80 border border-slate-800/80 hover:border-indigo-500/50 p-4 rounded-2xl shadow-md hover:shadow-indigo-500/10 transition-all cursor-grab active:cursor-grabbing group flex flex-col justify-between gap-3"
                    >
                      <p className="font-bold text-slate-200 text-xs leading-relaxed group-hover:text-white transition-colors">
                        {task.title}
                      </p>

                      <div className="flex justify-between items-center pt-2 border-t border-slate-900">
                        <div className="flex items-center gap-1.5">
                          <span className="w-5 h-5 rounded-full bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[9px] font-extrabold flex items-center justify-center">
                            IA
                          </span>
                          <span className="text-[10px] font-bold text-slate-400">{task.assigne || 'Enxame IA'}</span>
                        </div>

                        {/* BOTÃO EXCLUIR SEM CONFIRM DIALOG! */}
                        <button
                          onClick={() => handleDelete(task.id, task.title)}
                          className="text-slate-500 hover:text-red-400 p-1 rounded hover:bg-red-950/40 transition-colors text-xs font-bold"
                          title="Excluir Pauta"
                        >
                          ✕
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
