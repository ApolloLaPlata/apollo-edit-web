'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

export interface StoryData {
  id: string | number;
  title: string;
  slug: string;
  coverImage?: string;
  videoUrl?: string;
  blogName?: string;
}

export default function WebStoriesFeed({ stories, primaryColor = '#06b6d4' }: { stories: StoryData[], primaryColor?: string }) {
  const [activeStoryIdx, setActiveStoryIdx] = useState<number | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  if (!stories || stories.length === 0) return null;

  const openStory = (idx: number) => {
    setActiveStoryIdx(idx);
    document.body.style.overflow = 'hidden'; // Lock scroll
  };

  const closeStory = () => {
    setActiveStoryIdx(null);
    document.body.style.overflow = 'auto'; // Unlock scroll
  };

  const nextStory = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (activeStoryIdx !== null && activeStoryIdx < stories.length - 1) {
      setActiveStoryIdx(activeStoryIdx + 1);
    } else {
      closeStory();
    }
  };

  const prevStory = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (activeStoryIdx !== null && activeStoryIdx > 0) {
      setActiveStoryIdx(activeStoryIdx - 1);
    }
  };

  // Re-play video on change
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.currentTime = 0;
      videoRef.current.play().catch(e => console.log('Autoplay prevent:', e));
    }
  }, [activeStoryIdx]);

  return (
    <div className="w-full py-6 border-b border-theme-border/60 bg-theme-surface/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-2 mb-4">
          <span className="text-sm">🔥</span>
          <h2 className="text-sm font-extrabold uppercase tracking-widest text-theme-text">Web Stories</h2>
        </div>
        
        {/* Barra Horizontal (Thumbnails) */}
        <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
          {stories.map((story, idx) => (
            <div 
              key={story.id} 
              onClick={() => openStory(idx)}
              className="flex flex-col items-center gap-2 cursor-pointer shrink-0 snap-start group w-20 sm:w-24"
            >
              <div 
                className="w-16 h-16 sm:w-20 sm:h-20 rounded-full p-0.5 transition-transform group-hover:scale-105"
                style={{ background: `linear-gradient(45deg, #f59e0b, ${primaryColor}, #ec4899)` }}
              >
                <div className="w-full h-full rounded-full bg-theme-bg overflow-hidden border-2 border-theme-bg">
                  {story.coverImage ? (
                    <img src={story.coverImage} alt={story.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-slate-800 text-xl">📱</div>
                  )}
                </div>
              </div>
              <span className="text-[10px] font-bold text-theme-text text-center line-clamp-2 leading-tight">
                {story.title}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* MODAL TELA CHEIA (FULLSCREEN STORY) */}
      {activeStoryIdx !== null && (
        <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-xl flex items-center justify-center animate-in fade-in duration-200">
          
          <button onClick={closeStory} className="absolute top-6 right-6 z-50 w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center text-white backdrop-blur-md transition-colors">
            ✕
          </button>

          {/* Area do Video */}
          <div className="relative w-full max-w-[400px] h-[100dvh] sm:h-[80vh] sm:rounded-3xl overflow-hidden bg-slate-900 shadow-2xl flex flex-col">
            
            {/* Navigação Esquerda/Direita invisível para swipe click */}
            <div className="absolute inset-0 z-10 flex">
              <div className="w-1/3 h-full cursor-w-resize" onClick={prevStory} />
              <div className="w-2/3 h-full cursor-e-resize" onClick={nextStory} />
            </div>

            {/* Barra de Progresso Superior (Fake/Visual) */}
            <div className="absolute top-0 left-0 w-full p-4 z-30 flex gap-1.5">
              {stories.map((_, i) => (
                <div key={i} className="h-1 flex-1 bg-white/30 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-white transition-all duration-300"
                    style={{ width: i < activeStoryIdx ? '100%' : i === activeStoryIdx ? '50%' : '0%' }}
                  />
                </div>
              ))}
            </div>

            {/* Header do Story */}
            <div className="absolute top-8 left-0 w-full p-4 z-30 flex items-center gap-3">
               <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-white/50 bg-slate-800">
                 {stories[activeStoryIdx].coverImage && <img src={stories[activeStoryIdx].coverImage} className="w-full h-full object-cover" />}
               </div>
               <div>
                 <div className="text-white font-bold text-sm text-shadow-md">{stories[activeStoryIdx].blogName || 'Central'}</div>
                 <div className="text-white/70 text-[10px]">Patrocinado</div>
               </div>
            </div>

            {/* Midia do Story */}
            <div className="flex-1 w-full h-full bg-black relative">
              {stories[activeStoryIdx].videoUrl ? (
                <video 
                  ref={videoRef}
                  src={stories[activeStoryIdx].videoUrl}
                  className="w-full h-full object-cover"
                  autoPlay
                  playsInline
                  loop
                  muted={false}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center relative">
                  {stories[activeStoryIdx].coverImage && (
                     <img src={stories[activeStoryIdx].coverImage} className="absolute inset-0 w-full h-full object-cover opacity-50 blur-sm" />
                  )}
                  <div className="relative z-10 p-6 text-center">
                    <h3 className="text-2xl font-black text-white text-shadow-xl">{stories[activeStoryIdx].title}</h3>
                  </div>
                </div>
              )}
            </div>

            {/* Rodapé do Story (Call to Action) */}
            <div className="absolute bottom-0 left-0 w-full p-6 z-30 bg-gradient-to-t from-black via-black/70 to-transparent flex flex-col items-center gap-4">
               <div className="text-white font-bold text-center text-sm mb-2">{stories[activeStoryIdx].title}</div>
               <Link 
                 href={`/blog/${stories[activeStoryIdx].slug}`}
                 onClick={closeStory}
                 className="w-full py-3.5 rounded-full bg-white text-black font-extrabold text-sm text-center shadow-xl hover:scale-105 transition-transform"
               >
                 Ler Notícia Completa →
               </Link>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}
