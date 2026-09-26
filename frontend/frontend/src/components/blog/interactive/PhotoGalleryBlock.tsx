'use client';

import React, { useState } from 'react';

export interface PhotoItemData {
  url: string;
  caption?: string;
  credit?: string;
}

interface PhotoGalleryBlockProps {
  payload: {
    galleryTitle?: string;
    photos?: PhotoItemData[];
  };
  primaryColor?: string;
  secondaryColor?: string;
  accentStyle?: string;
}

export default function PhotoGalleryBlock({
  payload,
  primaryColor = '#06b6d4',
  secondaryColor = '#3b82f6',
  accentStyle = 'rounded'
}: PhotoGalleryBlockProps) {
  const galleryTitle = payload.galleryTitle || '📸 Galeria Exclusiva: Bastidores & Cobertura Visual';
  const photos: PhotoItemData[] = payload.photos || [
    {
      url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1000&q=80',
      caption: 'Arquitetura neural abstrata representando o processamento de dados do protocolo Colmeia.',
      credit: 'Foto: Studio Antigravity'
    },
    {
      url: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1000&q=80',
      caption: 'Terminais de controle e monitoramento contínuo em tempo real na base de operações.',
      credit: 'Foto: Tech Fleet'
    },
    {
      url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1000&q=80',
      caption: 'Linhas de código criptografadas e fluxos assíncronos gerados pela IA.',
      credit: 'Foto: Cyber Grid'
    },
    {
      url: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1000&q=80',
      caption: 'Estúdio de gravação audiovisual com setup de alta performance para canais dark.',
      credit: 'Foto: Dark Trap Radio'
    }
  ];

  const [activePhoto, setActivePhoto] = useState<PhotoItemData | null>(null);

  const radiusMap: Record<string, string> = {
    sharp: '0px',
    rounded: '16px',
    pill: '28px'
  };
  const radius = radiusMap[accentStyle] || '16px';

  return (
    <div className="my-10">
      {/* Header da Galeria */}
      <div className="flex items-center justify-between mb-4 pb-2 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-base">📸</span>
          <h3 className="text-sm md:text-base font-black uppercase tracking-wider text-white">
            {galleryTitle}
          </h3>
        </div>
        <span className="text-xs font-mono text-slate-400">
          {photos.length} fotos
        </span>
      </div>

      {/* Grade de Fotos (Mosaic Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 md:gap-4">
        {photos.map((photo, idx) => {
          const isFeatured = idx === 0 && photos.length > 2;
          return (
            <div
              key={idx}
              onClick={() => setActivePhoto(photo)}
              className={`group relative overflow-hidden cursor-pointer border border-slate-800/80 bg-slate-900/60 shadow-lg transition-all duration-300 hover:border-slate-600 hover:shadow-2xl ${
                isFeatured ? 'sm:col-span-2 md:col-span-2 md:row-span-2' : ''
              }`}
              style={{ borderRadius: radius }}
            >
              {/* Imagem */}
              <div className={`w-full overflow-hidden bg-slate-950 ${isFeatured ? 'h-64 sm:h-80 md:h-96' : 'h-48 md:h-52'}`}>
                <img
                  src={photo.url}
                  alt={photo.caption || `Foto ${idx + 1}`}
                  className="w-full h-full object-cover object-center transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                />
              </div>

              {/* Overlay com legenda */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex flex-col justify-end p-4">
                {photo.caption && (
                  <p className="text-xs text-white font-medium leading-tight mb-1 line-clamp-2">
                    {photo.caption}
                  </p>
                )}
                {photo.credit && (
                  <span className="text-[10px] font-mono text-slate-400 uppercase tracking-widest">
                    {photo.credit}
                  </span>
                )}
              </div>

              {/* Lupa ícone */}
              <div 
                className="absolute top-3 right-3 w-8 h-8 rounded-full bg-black/60 backdrop-blur-md flex items-center justify-center text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity border border-white/20"
              >
                🔍
              </div>
            </div>
          );
        })}
      </div>

      {/* Lightbox Modal (Sem native alerts/prompts) */}
      {activePhoto && (
        <div 
          onClick={() => setActivePhoto(null)}
          className="fixed inset-0 z-50 bg-black/95 backdrop-blur-2xl flex items-center justify-center p-4 md:p-8 animate-in fade-in duration-200"
        >
          <div 
            onClick={(e) => e.stopPropagation()}
            className="max-w-5xl w-full bg-slate-900 border border-slate-800 overflow-hidden shadow-2xl relative flex flex-col md:flex-row"
            style={{ borderRadius: radius }}
          >
            {/* Botão fechar */}
            <button
              onClick={() => setActivePhoto(null)}
              className="absolute top-4 right-4 z-10 w-10 h-10 rounded-full bg-black/80 hover:bg-black text-white font-bold text-lg flex items-center justify-center border border-white/20 transition-transform hover:scale-110"
            >
              ✕
            </button>

            {/* Imagem Expandida */}
            <div className="flex-1 bg-black flex items-center justify-center max-h-[75vh] md:max-h-[85vh] overflow-hidden">
              <img
                src={activePhoto.url}
                alt={activePhoto.caption || 'Zoom'}
                className="max-w-full max-h-full object-contain"
              />
            </div>

            {/* Legenda Lateral no Modal */}
            <div className="w-full md:w-80 p-6 bg-slate-950 flex flex-col justify-between border-t md:border-t-0 md:border-l border-slate-800">
              <div>
                <span className="text-[10px] font-black uppercase tracking-widest block mb-2" style={{ color: primaryColor }}>
                  ✨ Ampliação de Imagem
                </span>
                <p className="text-sm text-slate-200 font-medium leading-relaxed mb-4">
                  {activePhoto.caption || 'Sem legenda disponível.'}
                </p>
              </div>
              <div>
                {activePhoto.credit && (
                  <div className="text-xs font-mono text-slate-500 pt-4 border-t border-slate-800">
                    Créditos: <span className="text-slate-300">{activePhoto.credit}</span>
                  </div>
                )}
                <button
                  onClick={() => setActivePhoto(null)}
                  className="mt-4 w-full py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold transition-colors"
                >
                  Voltar ao Artigo
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
