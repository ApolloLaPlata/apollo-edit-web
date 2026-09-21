'use client';
import React, { useState, useEffect } from 'react';

function FallbackAd() {
  return (
    <div className="w-full max-w-4xl mx-auto my-10 relative z-10">
       <div className="w-full h-auto min-h-[90px] bg-theme-surface/50 border border-theme-border/60 rounded-2xl flex flex-col items-center justify-center overflow-hidden relative group shadow-lg cursor-pointer hover:shadow-2xl transition-all hover:scale-[1.01]">
         <img src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80&w=728&h=90&fit=crop" alt="Advertisement Mockup" className="w-full h-full object-cover opacity-90 group-hover:opacity-100 transition-opacity" />
         <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-md border border-white/10 px-2 py-0.5 rounded text-[9px] text-white/80 uppercase tracking-widest font-black">
           Ad
         </div>
       </div>
    </div>
  );
}

function renderHtmlWithAds(htmlStr: string, inTextAdHtml?: string) {
  // Dividir o HTML por parágrafos para podermos injetar os blocos de anúncios no meio
  const paragraphs = htmlStr.split('</p>');
  const totalParagraphs = paragraphs.length;
  
  // Fase 103: Cálculo Matemático Agressivo (Ad-Revenue)
  // Define o intervalo dinamicamente com base no tamanho do texto
  let adInterval = 3; 
  if (totalParagraphs > 15) {
    adInterval = 4; // Textos gigantes, respira um pouco mais
  } else if (totalParagraphs < 6) {
    adInterval = 2; // Textos curtos, monetização super agressiva
  }
  
  return paragraphs.map((p, idx) => {
    // Injetar anúncio a cada N parágrafos
    const isAdSpot = idx > 0 && idx % adInterval === 0 && idx < paragraphs.length - 1;
    
    // Remonta o parágrafo
    const paragraphHtml = p.trim() ? p + '</p>' : '';
    
    return (
       <React.Fragment key={idx}>
         {paragraphHtml && (
            <div 
              className="markdown-block mb-6 text-slate-300 font-medium tracking-wide text-lg leading-relaxed" 
              dangerouslySetInnerHTML={{ __html: paragraphHtml }} 
            />
         )}
         {isAdSpot && (
           inTextAdHtml ? (
             <div className="w-full max-w-4xl mx-auto my-10 relative z-10 block-ad" dangerouslySetInnerHTML={{ __html: inTextAdHtml }} />
           ) : (
             <FallbackAd />
           )
         )}
       </React.Fragment>
    );
  });
}

export default function PaywallBlocker({ contentHtml, inTextAdHtml, blogId }: { contentHtml: string, inTextAdHtml?: string, blogId?: string }) {
  const [isUnlocked, setIsUnlocked] = useState(true);
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  // Divide o conteúdo na tag do Paywall (Se inserida pelo redator IA)
  const parts = contentHtml.split('[PAYWALL]');
  const hasPaywall = parts.length > 1;

  useEffect(() => {
    if (hasPaywall) {
      const unlocked = localStorage.getItem('apollo_premium_unlocked') === 'true';
      setIsUnlocked(unlocked);
    }
  }, [hasPaywall]);

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setLoading(true);
    try {
      await fetch('/api/analytics/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, blogId })
      });
      localStorage.setItem('apollo_premium_unlocked', 'true');
      setIsUnlocked(true);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (!hasPaywall || isUnlocked) {
    return <>{renderHtmlWithAds(contentHtml.replace('[PAYWALL]', ''), inTextAdHtml)}</>;
  }

  return (
    <div className="relative">
      {/* Primeira parte (Aberta) */}
      <>{renderHtmlWithAds(parts[0], inTextAdHtml)}</>

      {/* Segunda parte (Borrada e Bloqueada) */}
      <div className="relative mt-8">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-theme-bg/80 to-theme-bg z-10 pointer-events-none"></div>
        <div className="blur-md select-none pointer-events-none opacity-30 h-[400px] overflow-hidden">
          <>{renderHtmlWithAds(parts[1].substring(0, 800) + '...', inTextAdHtml)}</>
        </div>

        {/* Caixa de Autenticação / Assinatura */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-20 w-full max-w-lg bg-theme-surface/80 backdrop-blur-3xl border border-theme-border/60 p-10 rounded-3xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] text-center group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-theme-accent/5 rounded-full blur-2xl -mr-16 -mt-16 pointer-events-none group-hover:bg-theme-accent/10 transition-colors" />
          
          <div className="w-20 h-20 bg-theme-accent/10 text-theme-accent rounded-full flex items-center justify-center text-4xl mx-auto mb-6 border border-theme-accent/30 shadow-[0_0_30px_rgba(var(--theme-accent-rgb),0.3)]">
            🔒
          </div>
          <h3 className="text-3xl font-black text-theme-text mb-3 tracking-tight">Leitura Restrita</h3>
          <p className="text-theme-muted text-base mb-8 font-medium">Cadastre-se gratuitamente para desbloquear este dossiê completo e receber nossas atualizações em primeira mão.</p>
          
          <form onSubmit={handleSubscribe} className="flex flex-col gap-4 relative z-10">
            <input 
              type="email" 
              placeholder="Seu melhor e-mail corporativo..." 
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-black/40 border border-theme-border/80 text-theme-text px-5 py-4 rounded-xl focus:border-theme-accent focus:shadow-[0_0_15px_rgba(var(--accent-rgb),0.3)] transition-all outline-none text-center font-semibold placeholder:text-theme-muted/50"
            />
            <button 
              type="submit" 
              disabled={loading}
              className="w-full bg-theme-accent hover:bg-theme-accent-hover text-white font-black py-4 rounded-xl transition-all shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.4)] hover:shadow-[0_0_25px_rgba(var(--theme-accent-rgb),0.6)] disabled:opacity-50 uppercase tracking-widest text-[11px]"
            >
              {loading ? 'Autenticando...' : 'Liberar Acesso Total'}
            </button>
          </form>
          <div className="flex items-center justify-center gap-2 mt-6">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
            <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Protocolo de Criptografia Ativo</p>
          </div>
        </div>
      </div>
    </div>
  );
}
