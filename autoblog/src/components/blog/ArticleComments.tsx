'use client';
import React, { useState } from 'react';
import { toast } from '@/components/ui/Toast';

interface CommentData {
  id?: number | string;
  authorName: string;
  authorAvatar: string;
  content: string;
  createdAt: string;
}

export default function ArticleComments({ initialComments }: { initialComments: CommentData[] }) {
  const [comments, setComments] = useState<CommentData[]>(initialComments);
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    
    // Simular o delay de rede para parecer mais real
    setTimeout(() => {
      const fakeComment: CommentData = {
        id: Date.now(),
        authorName: 'Visitante (Você)',
        authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=' + Date.now(),
        content: newComment,
        createdAt: new Date().toISOString(),
      };
      
      setComments([...comments, fakeComment]);
      setNewComment('');
      setIsSubmitting(false);
      
      // Feedback imediato
      toast.success('Seu comentário foi publicado com sucesso!');
    }, 600);
  };

  return (
    <div className="mb-12">
      <h3 className="text-2xl font-bold text-theme-text mb-6 flex items-center gap-2">
        <span className="text-theme-accent">💬</span> Discussão ({comments.length})
      </h3>
      
      <div className="space-y-6">
        {comments.map((comment, index) => (
          <div key={comment.id || index} className="bg-theme-surface/50 border border-theme-border p-6 rounded-2xl flex gap-4 animate-fade-in-up">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={comment.authorAvatar} alt={comment.authorName} loading="lazy" decoding="async" className="w-12 h-12 rounded-full border-2 border-theme-accent/50 flex-shrink-0" />
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h4 className="font-bold text-theme-text">{comment.authorName}</h4>
                <span className="text-xs text-theme-muted">{new Date(comment.createdAt).toLocaleDateString('pt-BR')}</span>
              </div>
              <p className="text-slate-300 text-sm">{comment.content}</p>
              <div className="flex gap-4 mt-3 text-xs font-bold text-slate-500">
                <button className="hover:text-theme-accent transition-colors">👍 Curtir</button>
                <button className="hover:text-theme-accent transition-colors">Responder</button>
              </div>
            </div>
          </div>
        ))}

        {comments.length === 0 && (
          <div className="text-center p-8 bg-theme-surface border border-theme-border rounded-2xl text-theme-muted">
            Ninguém comentou ainda. Seja o primeiro a opinar!
          </div>
        )}
      </div>
      
      {/* Caixa para usuário real comentar (Falsa interatividade instantânea) */}
      <div className="mt-8 bg-theme-surface p-6 rounded-2xl border border-theme-border flex gap-4 items-start">
         <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 border border-slate-600">👤</div>
         <form onSubmit={handleSubmit} className="w-full">
           <textarea 
             placeholder="Participe da discussão..." 
             className="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-slate-200 outline-none focus:border-theme-accent resize-none transition-colors" 
             rows={3}
             value={newComment}
             onChange={(e) => setNewComment(e.target.value)}
             required
           ></textarea>
           <div className="flex justify-end mt-2">
             <button 
               type="submit" 
               disabled={isSubmitting || !newComment.trim()}
               className="bg-theme-accent text-white px-6 py-2 rounded-lg font-bold text-sm hover:bg-theme-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
             >
               {isSubmitting ? 'Publicando...' : 'Publicar'}
             </button>
           </div>
         </form>
      </div>
    </div>
  );
}
