'use client';

import React, { useState } from 'react';

export interface VideoEpisodeData {
  title: string;
  duration?: string;
  youtubeId?: string;
  videoUrl?: string;
  thumbnail?: string;
  summary?: string;
}

interface VideoSeriesBlockProps {
  payload: {
    seriesTitle?: string;
    episodes?: VideoEpisodeData[];
  };
  primaryColor?: string;
  secondaryColor?: string;
  accentStyle?: string;
}

export default function VideoSeriesBlock({
  payload,
  primaryColor = '#3b82f6',
  secondaryColor = '#06b6d4',
  accentStyle = 'rounded'
}: VideoSeriesBlockProps) {
  const seriesTitle = payload.seriesTitle || 'Série Especial: Revolução da Inteligência Artificial (7 Episódios)';
  const episodes: VideoEpisodeData[] = payload.episodes || [
    {
      title: 'Episódio 1: O Despertar dos Modelos Neurais',
      duration: '12:40',
      youtubeId: 'dQw4w9WgXcQ', // fallback ou demo
      summary: 'Como os primeiros transformers mudaram o paradigma da sintaxe de código e jornalismo.'
    },
    {
      title: 'Episódio 2: A Arquitetura de Agentes Autônomos',
      duration: '15:20',
      youtubeId: 'jNQXAC9IVRw',
      summary: 'Os bastidores do protocolo Colmeia e a sincronização em tempo real.'
    },
    {
      title: 'Episódio 3: SEO Cauda Longa e Scraping Contínuo',
      duration: '09:15',
      youtubeId: 'L_LUpnjgPso',
      summary: 'A estratégia que garante pontuação 90+ no Core Web Vitals sem esforço manual.'
    },
    {
      title: 'Episódio 4: Designizações, Temas e Identidade Visual',
      duration: '14:50',
      youtubeId: 'dQw4w9WgXcQ',
      summary: 'Como manter 20 portais únicos com um único motor de backend.'
    }
  ];

  const [activeIdx, setActiveIdx] = useState(0);
  const activeEp = episodes[activeIdx] || episodes[0];

  const radiusMap: Record<string, string> = {
    sharp: '0px',
    rounded: '16px',
    pill: '28px'
  };
  const radius = radiusMap[accentStyle] || '16px';
  const pillRadius = accentStyle === 'sharp' ? '0px' : '9999px';

  return (
    <div 
      className="my-10 bg-slate-950 border-2 shadow-2xl relative overflow-hidden"
      style={{
        borderColor: `${primaryColor}40`,
        borderRadius: radius,
        boxShadow: `0 15px 40px -10px ${primaryColor}20`
      }}
    >
      {/* Top Banner */}
      <div className="p-4 md:p-5 bg-slate-900/90 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: primaryColor }} />
          <div>
            <span className="text-[10px] font-black uppercase tracking-widest block" style={{ color: primaryColor }}>
              🎬 Módulo de Vídeo em Série • Edição Exclusiva
            </span>
            <h3 className="text-base font-extrabold text-white leading-tight">
              {seriesTitle}
            </h3>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-slate-400 px-3 py-1 bg-slate-950 border border-slate-800" style={{ borderRadius: pillRadius }}>
            Episódio {activeIdx + 1} de {episodes.length}
          </span>
        </div>
      </div>

      {/* Main Grid: Player + Playlist */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
        
        {/* Vídeo / Embed (8 col) */}
        <div className="lg:col-span-8 bg-black flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800">
          <div className="relative w-full aspect-video bg-slate-900">
            {activeEp.youtubeId ? (
              <iframe
                src={`https://www.youtube.com/embed/${activeEp.youtubeId}?autoplay=0&rel=0`}
                title={activeEp.title}
                className="absolute inset-0 w-full h-full border-0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            ) : activeEp.videoUrl ? (
              <video
                src={activeEp.videoUrl}
                controls
                className="absolute inset-0 w-full h-full object-contain"
              />
            ) : (
              <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center bg-gradient-to-br from-slate-900 via-slate-950 to-black">
                <span className="text-5xl mb-3 animate-bounce">▶️</span>
                <h4 className="text-lg font-bold text-white mb-2">{activeEp.title}</h4>
                <p className="text-xs text-slate-400 max-w-md">{activeEp.summary}</p>
              </div>
            )}
          </div>

          {/* Info sob o player */}
          <div className="p-5 bg-slate-900/60">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-black uppercase tracking-wider text-white">
                {activeEp.title}
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                ⏱ {activeEp.duration || '10:00'}
              </span>
            </div>
            {activeEp.summary && (
              <p className="text-xs text-slate-400 leading-relaxed">
                {activeEp.summary}
              </p>
            )}
          </div>
        </div>

        {/* Playlist Lateral (4 col) */}
        <div className="lg:col-span-4 bg-slate-950 flex flex-col max-h-[460px] overflow-y-auto">
          <div className="p-3.5 bg-slate-900/40 border-b border-slate-800/80 text-[11px] font-extrabold uppercase tracking-widest text-slate-300 sticky top-0 z-10 backdrop-blur-md">
            📑 Lista de Capítulos
          </div>
          <div className="divide-y divide-slate-800/60 flex-1">
            {episodes.map((ep, idx) => {
              const isActive = activeIdx === idx;
              return (
                <button
                  key={idx}
                  onClick={() => setActiveIdx(idx)}
                  className={`w-full p-4 text-left transition-all flex items-start gap-3 group cursor-pointer ${
                    isActive ? 'bg-slate-900/90 text-white' : 'hover:bg-slate-900/40 text-slate-400 hover:text-slate-200'
                  }`}
                  style={isActive ? { borderLeft: `4px solid ${primaryColor}` } : { borderLeft: '4px solid transparent' }}
                >
                  {/* Número do episódio */}
                  <div 
                    className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-black shrink-0 transition-colors"
                    style={{
                      backgroundColor: isActive ? primaryColor : '#1e293b',
                      color: isActive ? '#fff' : '#94a3b8'
                    }}
                  >
                    {idx + 1}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-bold leading-snug line-clamp-2 group-hover:text-white mb-1">
                      {ep.title}
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-mono opacity-60">
                      <span>⏱ {ep.duration || '10:00'}</span>
                      {isActive && <span className="font-bold uppercase tracking-wider" style={{ color: primaryColor }}>• Em exibição</span>}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
}
