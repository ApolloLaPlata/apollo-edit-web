'use client';

import React, { useRef, useState } from 'react';
import Link from 'next/link';

export default function WebStories({ posts, domain }: { posts: any[], domain: string }) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [startX, setStartX] = useState(0);
  const [scrollLeft, setScrollLeft] = useState(0);

  // Fallback visual para posts sem imagem (placeholder IA)
  const getCoverImage = (post: any, index: number) => {
    if (post.coverImage) return post.coverImage;
    // Gerador determinístico de cores cyberpunk via HSL para fallback
    const hue = (index * 137.5) % 360;
    return `linear-gradient(135deg, hsl(${hue}, 80%, 40%), hsl(${(hue + 45) % 360}, 80%, 20%))`;
  };

  const onMouseDown = (e: React.MouseEvent) => {
    if (!scrollRef.current) return;
    setIsDragging(true);
    setStartX(e.pageX - scrollRef.current.offsetLeft);
    setScrollLeft(scrollRef.current.scrollLeft);
  };

  const onMouseLeave = () => setIsDragging(false);
  const onMouseUp = () => setIsDragging(false);

  const onMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !scrollRef.current) return;
    e.preventDefault();
    const x = e.pageX - scrollRef.current.offsetLeft;
    const walk = (x - startX) * 2; // Fast scroll multiplier
    scrollRef.current.scrollLeft = scrollLeft - walk;
  };

  // Pega no máximo os 8 primeiros posts para o feed de Stories
  const storyPosts = posts.slice(0, 8);
  
  if (storyPosts.length === 0) return null;

  return (
    <div className="w-full py-4 mb-6 relative group overflow-hidden">
      
      {/* Título do Segmento */}
      <div className="flex items-center gap-2 mb-4 px-4">
         <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
         <h2 className="text-sm font-black uppercase tracking-widest bg-[var(--text-color)]/80 bg-clip-text text-transparent">Trending Now</h2>
      </div>

      <div 
        ref={scrollRef}
        onMouseDown={onMouseDown}
        onMouseLeave={onMouseLeave}
        onMouseUp={onMouseUp}
        onMouseMove={onMouseMove}
        className="flex gap-4 overflow-x-auto px-4 pb-4 snap-x snap-mandatory hide-scrollbar cursor-grab active:cursor-grabbing"
        style={{ scrollBehavior: 'smooth', WebkitOverflowScrolling: 'touch' }}
      >
        {storyPosts.map((post, i) => (
          <Link 
            key={post.id || i}
            href={`http://${domain}/blog/${post.slug}`}
            className="flex-shrink-0 snap-center relative w-[110px] h-[190px] rounded-2xl overflow-hidden group/story transition-transform hover:scale-105 shadow-xl ring-2 ring-offset-2 ring-offset-[var(--bg-color)] ring-transparent hover:ring-[var(--accent-color)]"
            style={{ 
              boxShadow: '0 10px 25px -5px rgba(0,0,0, 0.5)'
            }}
          >
            {/* Background Image / Gradient Fallback */}
            {post.coverImage ? (
              <img 
                src={post.coverImage} 
                alt={post.title} 
                className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover/story:scale-110"
              />
            ) : (
              <div 
                className="absolute inset-0 w-full h-full opacity-80"
                style={{ background: getCoverImage(post, i) }}
              />
            )}
            
            {/* Vignette Overlay (Dark bottom for text readability) */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent"></div>
            
            {/* Story Indicator bar */}
            <div className="absolute top-2 left-2 right-2 flex gap-1 z-10">
              <div className="h-1 bg-white/30 rounded-full flex-1 overflow-hidden">
                <div className="h-full bg-white w-0 group-hover/story:w-full transition-all duration-3000 ease-linear"></div>
              </div>
            </div>

            {/* Title */}
            <div className="absolute bottom-3 left-3 right-3 z-10">
              <p className="text-white text-[10px] font-black leading-tight line-clamp-3 filter drop-shadow-md">
                {post.title}
              </p>
            </div>
            
            {/* Play Button Hologram */}
            <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/story:opacity-100 transition-opacity z-20 backdrop-blur-[2px] bg-black/20">
               <div className="w-8 h-8 rounded-full bg-[var(--accent-color)] flex items-center justify-center shadow-[0_0_15px_var(--accent-color)] pl-1">
                 <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4l12 6-12 6z"/></svg>
               </div>
            </div>
          </Link>
        ))}
      </div>
      
      {/* Estilo Injetado (escondendo scrollbar) */}
      <style dangerouslySetInnerHTML={{__html: `
        .hide-scrollbar::-webkit-scrollbar { display: none; }
        .hide-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}} />
    </div>
  );
}
