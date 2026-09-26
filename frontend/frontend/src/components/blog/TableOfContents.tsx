'use client';
import React, { useEffect, useState, useRef } from 'react';
import GithubSlugger from 'github-slugger';

type Heading = {
  id: string;
  text: string;
  level: number;
};

export default function TableOfContents({ contentMd }: { contentMd: string }) {
  const [headings, setHeadings] = useState<Heading[]>([]);
  const [activeId, setActiveId] = useState<string>('');
  const observerRef = useRef<IntersectionObserver | null>(null);

  // 1. Extrair Headings e seus IDs (Simulando o rehype-slug)
  useEffect(() => {
    const slugger = new GithubSlugger();
    const regex = /^(#{2,3})\s+(.+)$/gm;
    let match;
    const extractedHeadings: Heading[] = [];
    
    while ((match = regex.exec(contentMd)) !== null) {
      const level = match[1].length;
      const text = match[2].replace(/\*/g, '').replace(/`/g, '');
      const id = slugger.slug(text);
      extractedHeadings.push({ id, text, level });
    }
    
    setHeadings(extractedHeadings);
  }, [contentMd]);

  // 2. IntersectionObserver para saber qual Heading está visível
  useEffect(() => {
    if (headings.length === 0) return;

    // Atrasar a observação um pouquinho para garantir que o DOM já montou o HTML
    const timer = setTimeout(() => {
      const headingElements = Array.from(document.querySelectorAll('.zen-article h2, .zen-article h3'));
      
      observerRef.current = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setActiveId(entry.target.id);
            }
          });
        },
        { rootMargin: '-10% 0px -80% 0px', threshold: 1.0 } // Dispara quando o titulo passa pelo top 10% da tela
      );

      headingElements.forEach((el) => {
        if (el.id) observerRef.current?.observe(el);
      });
    }, 500);

    return () => {
      clearTimeout(timer);
      observerRef.current?.disconnect();
    };
  }, [headings]);

  if (headings.length === 0) return null;

  // 3. Scroll Suave
  const scrollToHeading = (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    const target = document.getElementById(id);
    if (target) {
      // Compensa a altura do menu superior fixo (se houver)
      const offset = 100;
      const targetPosition = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({
        top: targetPosition,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="bg-theme-surface/80 backdrop-blur-md p-6 rounded-2xl border border-theme-border/60 shadow-xl sticky top-24">
      <h3 className="text-theme-text font-black mb-4 uppercase tracking-widest text-sm flex items-center gap-2">
        <span className="w-2 h-4 bg-theme-accent rounded-sm inline-block"></span>
        Nesta Matéria
      </h3>
      <nav className="space-y-3 relative">
        {/* Linha vertical que conecta os pontos (UI Premium) */}
        <div className="absolute left-1.5 top-2 bottom-2 w-px bg-theme-border/50"></div>
        
        {headings.map((h, i) => {
          const isActive = activeId === h.id;
          return (
            <div key={i} className={`relative flex items-center gap-3 ${h.level === 3 ? 'ml-4' : ''}`}>
               {/* Bolinha indicadora de estado */}
               <div className={`w-3 h-3 rounded-full border-2 z-10 transition-colors duration-300 ${isActive ? 'bg-theme-accent border-theme-accent shadow-[0_0_10px_rgba(var(--theme-accent-rgb),0.8)]' : 'bg-theme-surface border-theme-border'}`}></div>
               
               <a 
                 href={`#${h.id}`}
                 onClick={(e) => scrollToHeading(e, h.id)}
                 className={`block text-sm transition-all duration-300 flex-1 leading-snug ${isActive ? 'font-bold text-theme-accent scale-[1.02] origin-left' : 'font-medium text-slate-500 hover:text-slate-300'}`}
               >
                 {h.text}
               </a>
            </div>
          );
        })}
      </nav>
    </div>
  );
}
