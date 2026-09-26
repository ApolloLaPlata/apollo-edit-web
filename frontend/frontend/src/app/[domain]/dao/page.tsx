import React from 'react';
import db from '@/lib/db';
import Link from 'next/link';

// Componente Cliente Interno para lidar com o voto
import DaoVoteClient from './DaoVoteClient';

export default function DaoPage({ params }: { params: { domain: string } }) {
  // Buscar os tópicos pendentes do banco
  let topics: any[] = [];
  try {
    topics = db.prepare(`SELECT * FROM DaoTopic WHERE status = 'pending' ORDER BY votes DESC`).all();
  } catch (err) {
    console.error('Erro ao buscar DAO Topics:', err);
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-300 font-sans selection:bg-cyan-500/30">
      <div className="max-w-4xl mx-auto px-6 py-16 animate-in fade-in duration-700">
        
        {/* Header do DAO */}
        <div className="mb-12 text-center relative">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
          <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter mb-4 relative z-10">
            A Inteligência é <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Descentralizada</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto relative z-10 leading-relaxed">
            Nossos agentes autônomos escaneiam o submundo da web em busca de pautas. 
            Você decide o que eles vão investigar a seguir. <strong>A pauta que bater 100 votos ganha uma matéria completa e um podcast.</strong>
          </p>
        </div>

        {/* Lista de Pautas */}
        <div className="space-y-6 relative z-10">
          {topics.length === 0 ? (
            <div className="p-12 text-center border border-slate-800 rounded-3xl bg-slate-900/50 backdrop-blur-xl">
              <span className="text-4xl mb-4 block">🤖</span>
              <h3 className="text-xl font-bold text-white mb-2">A Mente Colmeia está processando...</h3>
              <p className="text-slate-500">Nenhuma pauta pendente no momento. Os agentes estão caçando novos rumores.</p>
            </div>
          ) : (
            topics.map((topic) => (
              <DaoVoteClient key={topic.id} topic={topic} />
            ))
          )}
        </div>

        <div className="mt-16 text-center border-t border-slate-800/60 pt-8">
          <Link href="/" className="text-cyan-500 hover:text-cyan-400 font-semibold transition-colors">
            ← Voltar para as Notícias
          </Link>
        </div>
      </div>
    </div>
  );
}
