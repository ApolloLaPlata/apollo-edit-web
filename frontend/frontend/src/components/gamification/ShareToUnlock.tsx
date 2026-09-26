'use client';

import React, { useState } from 'react';

/**
 * 📲 GATILHO DE VIRALIDADE (Share to Unlock)
 * Esconde uma fofoca crítica e obriga o leitor a compartilhar o link no Zap 
 * para revelar o segredo. Se a matéria for boa, gera dezenas de acessos gratuitos.
 */
export default function ShareToUnlock({ secretContent, shareUrl, shareText }: { secretContent: string, shareUrl: string, shareText: string }) {
  const [unlocked, setUnlocked] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleShare = () => {
    setLoading(true);
    
    // Monta o Link do WhatsApp (Mobile/Desktop)
    const zapLink = `https://api.whatsapp.com/send?text=${encodeURIComponent(shareText + ' ' + shareUrl)}`;
    
    // Abre no Zap em Nova Aba
    window.open(zapLink, '_blank');
    
    // Simula a espera de que a pessoa realmente compartilhou
    setTimeout(() => {
      setLoading(false);
      setUnlocked(true);
      
      // Dispara o evento de Gamificação (XP Extra!)
      if (typeof window !== 'undefined') {
        const event = new CustomEvent('earn_xp', { detail: 150 });
        window.dispatchEvent(event);
      }
    }, 4000); // 4 Segundos é o tempo médio que o cara vai no zap e volta
  };

  if (unlocked) {
    return (
      <div className="my-8 p-6 bg-red-50 dark:bg-slate-900/50 border-l-4 border-red-500 rounded-r-2xl animate-in zoom-in-95 duration-500">
        <span className="text-xs uppercase font-black tracking-widest text-red-500 mb-2 block">🔒 Segredo Revelado</span>
        <div className="prose dark:prose-invert text-slate-800 dark:text-slate-200">
           {secretContent}
        </div>
      </div>
    );
  }

  return (
    <div className="my-8 relative rounded-3xl overflow-hidden border border-slate-200 dark:border-slate-800 shadow-xl group">
      
      {/* Texto Escondido / Borrado Atrás */}
      <div className="p-8 pb-12 blur-md opacity-30 pointer-events-none select-none bg-slate-100 dark:bg-slate-900/30">
        {secretContent}
      </div>

      <div className="absolute inset-0 bg-gradient-to-t from-white via-white/80 dark:from-slate-950 dark:via-slate-950/80 to-transparent flex flex-col items-center justify-center p-6 text-center">
        
        <span className="text-5xl mb-4 group-hover:scale-110 transition-transform">🤫</span>
        
        <h3 className="text-xl md:text-2xl font-black text-slate-900 dark:text-white mb-2">
          Final Chocante Bloqueado
        </h3>
        
        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 font-medium max-w-sm">
          Mande essa fofoca para um amigo(a) no WhatsApp para ler o verdadeiro final da história e ganhar <span className="text-red-500 font-bold">+150 XP</span>.
        </p>
        
        <button 
          onClick={handleShare}
          disabled={loading}
          className="bg-[#25D366] hover:bg-[#128C7E] text-white font-bold py-4 px-8 rounded-xl flex items-center justify-center gap-3 transition-colors shadow-lg shadow-green-600/30 w-full max-w-xs"
        >
          {loading ? (
             <span className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.006c.106.005.249-.04.39.298.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.86s.274.072.376-.043c.101-.116.433-.506.549-.68.116-.173.231-.145.39-.087s1.011.477 1.184.564.289.13.332.202c.045.072.045.419-.1.824zm-3.423-14.416c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm.082 21.369c-1.42 0-2.812-.363-4.041-1.05l-4.496 1.18 1.198-4.382c-.754-1.266-1.152-2.73-1.151-4.225.003-4.604 3.748-8.349 8.356-8.349 2.232.001 4.331.87 5.908 2.45 1.577 1.579 2.446 3.679 2.445 5.91-.004 4.604-3.75 8.348-8.355 8.348z"/></svg>
              Destravar com WhatsApp
            </>
          )}
        </button>
      </div>
    </div>
  );
}
