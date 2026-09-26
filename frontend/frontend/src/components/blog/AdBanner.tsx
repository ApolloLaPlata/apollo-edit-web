import React from 'react';
import db from '@/lib/db';
import AdRenderer from './AdRenderer';

export default async function AdBanner({ type = 'horizontal', domain }: { type?: 'horizontal' | 'vertical' | 'square' | 'in_feed' | 'sidebar', domain?: string }) {
  const isHorizontal = type === 'horizontal';
  const isSquare = type === 'square' || type === 'sidebar';
  const isInFeed = type === 'in_feed';
  
  const widthClass = isHorizontal || isInFeed ? 'w-full max-w-4xl' : (isSquare ? 'w-full max-w-[300px]' : 'w-full max-w-[300px]');
  const heightClass = isHorizontal || isInFeed ? 'h-auto min-h-[90px]' : (isSquare ? 'h-auto min-h-[250px]' : 'h-auto min-h-[600px]');

  let adContent = null;
  
  // Mapeamento do tipo antigo para as posições do AdBlock
  let mappedPosition = 'sidebar';
  if (type === 'horizontal') mappedPosition = 'article_top';
  if (type === 'in_feed') mappedPosition = 'article_middle';

  const adRaw = db.prepare(`
    SELECT scriptCode 
    FROM AdBlock
    WHERE position = ? AND isActive = 1
    LIMIT 1
  `).get(mappedPosition) as any;
  
  if (adRaw) {
    adContent = adRaw.scriptCode;
  }

  if (adContent) {
    return (
      <AdRenderer className={`mx-auto my-8 ${widthClass} overflow-hidden`} html={adContent} />
    );
  }

  // Mockups visuais de Adsense (728x90 para horizontal, 300x250 para sidebar)
  const adImage = isHorizontal || isInFeed 
    ? 'https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=728&h=90&fit=crop' // Banner Largo (Marketing/Dados)
    : 'https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=300&h=250&fit=crop'; // Banner Quadrado (Gadget/Tech)

  return (
    <div className={`mx-auto my-8 ${widthClass} ${heightClass} bg-theme-surface/50 border border-theme-border/60 rounded-2xl flex flex-col items-center justify-center overflow-hidden relative group shadow-lg cursor-pointer hover:shadow-2xl transition-all hover:scale-[1.01]`}>
      <img src={adImage} alt="Advertisement Mockup" className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity" />
      <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-md border border-white/10 px-2 py-0.5 rounded text-[9px] text-white/80 uppercase tracking-widest font-black">
        Ad
      </div>
      <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000 pointer-events-none"></div>
    </div>
  );
}
