'use client';
import React, { useState } from 'react';

const REACTIONS = [
  { id: 'fire', emoji: '🔥', label: 'Incrível', color: 'text-orange-500', bg: 'bg-orange-500/10' },
  { id: 'mindblown', emoji: '🤯', label: 'Mindblown', color: 'text-purple-500', bg: 'bg-purple-500/10' },
  { id: 'useful', emoji: '💡', label: 'Útil', color: 'text-yellow-500', bg: 'bg-yellow-500/10' },
  { id: 'angry', emoji: '😡', label: 'Revolta', color: 'text-red-500', bg: 'bg-red-500/10' }
];

export default function ArticleReactions({ postId }: { postId: string }) {
  const [active, setActive] = useState<string | null>(null);
  const [counts, setCounts] = useState<Record<string, number>>({
    fire: Math.floor(Math.random() * 50) + 12,
    mindblown: Math.floor(Math.random() * 20) + 3,
    useful: Math.floor(Math.random() * 80) + 20,
    angry: Math.floor(Math.random() * 5)
  });

  const handleReact = (id: string) => {
    if (active === id) return;
    
    setCounts(prev => ({
      ...prev,
      [id]: prev[id] + 1,
      ...(active ? { [active]: prev[active] - 1 } : {})
    }));
    setActive(id);
  };

  return (
    <div className="w-full bg-theme-surface/60 border border-theme-border p-6 rounded-2xl flex flex-col items-center justify-center gap-4 my-8 shadow-inner">
      <h3 className="text-sm font-black uppercase tracking-widest text-theme-muted">Qual a sua reação?</h3>
      <div className="flex flex-wrap items-center justify-center gap-3 md:gap-6">
        {REACTIONS.map((r) => {
          const isActive = active === r.id;
          return (
            <button
              key={r.id}
              onClick={() => handleReact(r.id)}
              className={`flex flex-col items-center gap-1.5 p-3 rounded-2xl transition-all duration-300 ${isActive ? `${r.bg} scale-110 shadow-lg` : 'hover:bg-black/20 border border-transparent'}`}
            >
              <span className={`text-3xl md:text-4xl ${isActive ? 'animate-bounce' : 'grayscale-[50%] hover:grayscale-0'} transition-all`}>
                {r.emoji}
              </span>
              <span className={`text-[10px] font-black uppercase tracking-wider ${isActive ? r.color : 'text-theme-muted'}`}>
                {r.label}
              </span>
              <span className={`text-xs font-mono font-bold ${isActive ? 'text-white' : 'text-theme-muted/60'}`}>
                {counts[r.id]}
              </span>
            </button>
          );
        })}
      </div>
      {active && (
        <div className="text-xs font-bold text-theme-accent animate-pulse mt-2">
          Feedback registrado anonimamente!
        </div>
      )}
    </div>
  );
}
