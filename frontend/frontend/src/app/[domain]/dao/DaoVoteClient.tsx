'use client';

import React, { useState } from 'react';

export default function DaoVoteClient({ topic }: { topic: any }) {
  const [votes, setVotes] = useState(topic.votes || 0);
  const [status, setStatus] = useState(topic.status);
  const [loading, setLoading] = useState(false);
  const [voted, setVoted] = useState(false);

  const handleVote = async () => {
    if (voted || loading || status === 'approved') return;
    setLoading(true);
    try {
      const res = await fetch('/api/dao/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topicId: topic.id })
      });
      const data = await res.json();
      if (data.success) {
        setVotes(data.votes);
        setStatus(data.status);
        setVoted(true);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const progress = Math.min((votes / 100) * 100, 100);

  return (
    <div className="bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 p-6 md:p-8 rounded-3xl shadow-xl flex flex-col md:flex-row gap-6 items-center group hover:border-slate-700/80 transition-colors relative overflow-hidden">
      
      {/* Background Progress Layer */}
      <div 
        className="absolute inset-y-0 left-0 bg-cyan-900/10 z-0 transition-all duration-1000 ease-out"
        style={{ width: `${progress}%` }}
      />

      <div className="flex-1 relative z-10">
        <div className="flex items-center gap-3 mb-2">
          <span className="px-2.5 py-1 rounded-md bg-slate-800 text-[10px] font-bold text-slate-400 uppercase tracking-widest font-mono">
            {topic.id}
          </span>
          {status === 'approved' && (
            <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 text-[10px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Em Redação
            </span>
          )}
        </div>
        <h2 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-400 transition-colors">{topic.title}</h2>
        <p className="text-sm text-slate-400 leading-relaxed">{topic.description}</p>
      </div>

      <div className="flex flex-col items-center gap-3 relative z-10 w-full md:w-auto shrink-0">
        <button
          onClick={handleVote}
          disabled={voted || status === 'approved'}
          className={`w-full md:w-40 py-3 rounded-2xl font-bold transition-all shadow-lg flex items-center justify-center gap-2
            ${status === 'approved' 
              ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/30 opacity-70 cursor-not-allowed' 
              : voted 
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' 
                : 'bg-white text-slate-900 hover:bg-slate-200 hover:scale-105 active:scale-95'
            }`}
        >
          {loading ? (
             <span className="w-5 h-5 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
          ) : status === 'approved' ? (
            '✓ APROVADO'
          ) : voted ? (
            '✓ VOTADO'
          ) : (
            '⇧ VOTAR'
          )}
        </button>
        
        <div className="w-full text-center">
          <div className="text-2xl font-black text-white font-mono tracking-tighter">
            {votes}<span className="text-sm text-slate-500 font-sans tracking-normal font-normal">/100</span>
          </div>
          <div className="w-full bg-slate-950 rounded-full h-1.5 mt-2 border border-slate-800">
            <div 
              className={`h-full rounded-full transition-all duration-700 ${status === 'approved' ? 'bg-emerald-500' : 'bg-cyan-500 shadow-[0_0_10px_rgba(6,182,212,0.5)]'}`}
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
