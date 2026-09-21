'use client';

import React, { useState, useEffect } from 'react';

/**
 * Sistema de Comentários Híbrido (Ghost + Real)
 * Renderiza comentários injetados pelo Motor Fantasma da IA ou estáticos simulados.
 */
export default function GhostComments({ postId, domain }: { postId: string, domain: string }) {
  const [comments, setComments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simula a busca de comentários no banco ou carrega os Ghosts injetados pela IA na matéria
    // Em produção real com o Auto-Blog, faremos fetch(`/api/comments?postId=${postId}`)
    setTimeout(() => {
      setComments([
        { id: 1, name: 'Carlos Henrique', time: 'Há 2 horas', text: 'Excelente matéria. Eu já desconfiava disso há um tempo, impressionante como esconderam a verdade.', likes: 14, avatar: 'CH' },
        { id: 2, name: 'Marina Silva_89', time: 'Há 5 horas', text: 'Não acredito em uma palavra disso. Só vou acreditar vendo as provas originais...', likes: 2, avatar: 'M' },
        { id: 3, name: 'João P. Oficial', time: 'Há 12 horas', text: 'Compartilhei no meu grupo de zap, o pessoal surtou com a novidade kkkkkkk valeu!', likes: 45, avatar: 'JP' },
      ]);
      setLoading(false);
    }, 1200);
  }, [postId]);

  return (
    <section className="mt-16 pt-10 border-t border-slate-200 dark:border-slate-800">
      <div className="flex items-center justify-between mb-8">
        <h3 className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-2">
          <span className="w-1.5 h-6 bg-red-600 inline-block rounded-sm"></span>
          Discussão Aberta
        </h3>
        <span className="text-sm font-bold text-slate-400 bg-slate-100 dark:bg-slate-900 px-3 py-1 rounded-full">
          {comments.length} Comentários
        </span>
      </div>

      {/* CAIXA DE INPUT */}
      <div className="flex gap-4 mb-10">
        <div className="w-12 h-12 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center shrink-0 font-bold text-slate-400">
          Você
        </div>
        <div className="flex-1 relative">
          <textarea 
            placeholder="Deixe sua opinião impopular aqui..." 
            className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 min-h-[100px] outline-none focus:border-red-500/50 focus:ring-4 focus:ring-red-500/10 transition-all text-sm resize-none text-slate-700 dark:text-slate-300"
          ></textarea>
          <button className="absolute bottom-3 right-3 bg-slate-900 dark:bg-red-600 text-white text-xs font-bold uppercase tracking-wider px-4 py-2 rounded-lg hover:bg-slate-800 dark:hover:bg-red-500 transition-colors">
            Comentar
          </button>
        </div>
      </div>

      {/* FEED DE GHOSTS */}
      {loading ? (
        <div className="space-y-6 animate-pulse">
           {[1,2].map(i => (
             <div key={i} className="flex gap-4">
               <div className="w-10 h-10 bg-slate-200 dark:bg-slate-800 rounded-full"></div>
               <div className="flex-1 space-y-2 py-1">
                 <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-1/4"></div>
                 <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-3/4"></div>
               </div>
             </div>
           ))}
        </div>
      ) : (
        <div className="space-y-8">
          {comments.map((comment) => (
            <div key={comment.id} className="flex gap-4 group">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center font-bold text-slate-600 dark:text-slate-400 text-xs shrink-0 border border-white dark:border-slate-800 shadow-sm">
                {comment.avatar}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-bold text-sm text-slate-800 dark:text-slate-200">{comment.name}</span>
                  <span className="text-xs text-slate-400">• {comment.time}</span>
                </div>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  {comment.text}
                </p>
                <div className="flex items-center gap-4 mt-2">
                  <button className="text-xs font-semibold text-slate-400 hover:text-red-500 transition-colors flex items-center gap-1">
                    👍 {comment.likes}
                  </button>
                  <button className="text-xs font-semibold text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors">
                    Responder
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <button className="w-full mt-8 py-3 border border-slate-200 dark:border-slate-800 text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-xl text-sm font-bold transition-colors">
        Carregar Mais Comentários
      </button>
    </section>
  );
}
