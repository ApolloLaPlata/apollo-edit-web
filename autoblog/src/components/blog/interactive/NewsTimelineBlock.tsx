'use client';

import React, { useState } from 'react';

export interface TimelineNodeData {
  timeLabel: string;
  title: string;
  summary: string;
  tag?: string;
  isHighlight?: boolean;
}

interface NewsTimelineBlockProps {
  payload: {
    timelineTitle?: string;
    nodes?: TimelineNodeData[];
  };
  primaryColor?: string;
  secondaryColor?: string;
  accentStyle?: string;
}

export default function NewsTimelineBlock({
  payload,
  primaryColor = '#10b981',
  secondaryColor = '#06b6d4',
  accentStyle = 'rounded'
}: NewsTimelineBlockProps) {
  const timelineTitle = payload.timelineTitle || '⏱️ Linha do Tempo: Correlação de Fatos & Evolução da Notícia';
  const nodes: TimelineNodeData[] = payload.nodes || [
    {
      timeLabel: 'Ontem · 14:30',
      title: 'Primeiro Alerta do Banco Central',
      summary: 'Comunicado oficial aponta para necessidade de regulamentação imediata de protocolos descentralizados e inteligência autônoma.',
      tag: 'Origem',
      isHighlight: false
    },
    {
      timeLabel: 'Hoje · 08:00',
      title: 'Reação dos Mercados & Ações Tech',
      summary: 'Bolsas asiáticas e europeias abrem em alta puxadas pelo setor de semicondutores e servidores de processamento neural.',
      tag: 'Mercado',
      isHighlight: false
    },
    {
      timeLabel: 'Hoje · 11:45',
      title: 'Pronunciamento Conjunto da Frota Antigravity',
      summary: 'A diretoria da rede confirma a sincronização total da colmeia e o acionamento de relatórios em tempo real sem falhas de memória.',
      tag: 'Breaking',
      isHighlight: true
    },
    {
      timeLabel: 'Agora · Em Andamento',
      title: 'Implementação de Módulos Interativos no CMS',
      summary: 'Deploy ao vivo da arquitetura que permite a cada site exibir players, galerias e timelines geradas autonomamente por IA.',
      tag: 'Evolução',
      isHighlight: true
    }
  ];

  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  const radiusMap: Record<string, string> = {
    sharp: '0px',
    rounded: '16px',
    pill: '28px'
  };
  const radius = radiusMap[accentStyle] || '16px';
  const pillRadius = accentStyle === 'sharp' ? '0px' : '9999px';

  return (
    <div 
      className="my-10 p-6 md:p-8 bg-slate-900/80 border-2 shadow-2xl relative overflow-hidden backdrop-blur-md"
      style={{
        borderColor: `${primaryColor}40`,
        borderRadius: radius
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <span className="w-3 h-3 rounded-full animate-pulse" style={{ backgroundColor: primaryColor }} />
          <div>
            <span className="text-[10px] font-black uppercase tracking-widest block" style={{ color: primaryColor }}>
              📑 Jornalismo de Contexto • Correlação Cronológica
            </span>
            <h3 className="text-base md:text-lg font-black text-white">
              {timelineTitle}
            </h3>
          </div>
        </div>
        <span 
          className="text-[10px] font-mono font-bold px-3 py-1 uppercase tracking-wider text-white border border-white/10"
          style={{ backgroundColor: `${primaryColor}20`, borderRadius: pillRadius }}
        >
          {nodes.length} Eventos
        </span>
      </div>

      {/* Timeline Tree */}
      <div className="relative pl-6 md:pl-8 border-l-2 border-slate-800 space-y-8 ml-2 md:ml-4">
        {nodes.map((node, idx) => {
          const isExp = expandedIdx === idx;
          return (
            <div key={idx} className="relative group">
              {/* Timeline Dot */}
              <div 
                className="absolute -left-[31px] md:-left-[39px] top-1.5 w-4 h-4 md:w-5 md:h-5 rounded-full border-4 border-slate-900 transition-transform duration-300 group-hover:scale-125"
                style={{
                  backgroundColor: node.isHighlight ? primaryColor : '#475569',
                  boxShadow: node.isHighlight ? `0 0 12px ${primaryColor}` : undefined
                }}
              />

              {/* Node Card */}
              <div 
                onClick={() => setExpandedIdx(isExp ? null : idx)}
                className={`p-4 md:p-5 border transition-all cursor-pointer ${
                  node.isHighlight 
                    ? 'bg-slate-900/90 border-opacity-80 shadow-xl' 
                    : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-900/50 hover:border-slate-700'
                }`}
                style={{
                  borderRadius: radius,
                  borderColor: node.isHighlight ? primaryColor : undefined
                }}
              >
                {/* Node Header */}
                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-slate-400">
                      🕒 {node.timeLabel}
                    </span>
                    {node.tag && (
                      <span 
                        className="text-[9px] font-extrabold uppercase px-2 py-0.5"
                        style={{
                          backgroundColor: node.isHighlight ? `${primaryColor}25` : '#1e293b',
                          color: node.isHighlight ? primaryColor : '#cbd5e1',
                          borderRadius: pillRadius
                        }}
                      >
                        {node.tag}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-slate-500 font-mono">
                    {isExp ? '− Ocultar detalhes' : '+ Ver correlação'}
                  </span>
                </div>

                {/* Title */}
                <h4 className="text-sm md:text-base font-extrabold text-white leading-snug group-hover:text-cyan-300 transition-colors">
                  {node.title}
                </h4>

                {/* Summary (Expandível ou sempre visível) */}
                <p className={`text-xs md:text-sm text-slate-300 leading-relaxed mt-2.5 transition-all ${
                  isExp ? 'block' : 'line-clamp-2 opacity-80'
                }`}>
                  {node.summary}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer Dica */}
      <div className="mt-6 pt-4 border-t border-slate-800/60 text-center text-[11px] font-mono text-slate-500">
        💡 Clique em qualquer fato da linha do tempo para expandir os detalhes e entender a correlação da notícia.
      </div>
    </div>
  );
}
