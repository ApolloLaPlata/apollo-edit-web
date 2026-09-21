'use client';
import { useEffect } from 'react';

export default function InteractiveBlockquotes() {
  useEffect(() => {
    // Procura todos os blockquotes gerados pelo Markdown da IA
    const blockquotes = document.querySelectorAll('.zen-article blockquote');
    
    blockquotes.forEach((bq) => {
      // Evita instrumentar o mesmo elemento duas vezes (em re-renders)
      if (bq.querySelector('.twitter-share-btn')) return;

      // O texto bruto da citação para mandar pro Twitter
      const text = bq.textContent || '';
      
      // Corta o texto se for muito gigante (limite do Twitter)
      const truncatedText = text.length > 200 ? text.substring(0, 197) + '...' : text;
      const shareText = encodeURIComponent(`"${truncatedText.trim()}"`);
      const shareUrl = encodeURIComponent(window.location.href);

      // Injeta classes Tailwind avançadas no blockquote (o rawHtml do rehype apenas joga <blockquote> limpo)
      bq.classList.add(
        'relative', 'my-10', 'pl-10', 'pr-6', 'py-8', 
        'bg-slate-900/40', 'backdrop-blur-md', 'border-l-4', 'border-theme-accent', 
        'rounded-r-2xl', 'text-xl', 'md:text-2xl', 'font-medium', 'italic', 'text-slate-200', 
        'shadow-xl', 'leading-relaxed'
      );

      // Remove a margem bottom do parágrafo interno para ficar alinhado
      const p = bq.querySelector('p');
      if (p) p.classList.add('mb-0');

      // Container do botão
      const btnContainer = document.createElement('div');
      btnContainer.className = 'mt-6 flex justify-end twitter-share-btn relative z-10';
      
      // Botão de Compartilhar do Twitter/X
      const shareBtn = document.createElement('a');
      shareBtn.href = `https://twitter.com/intent/tweet?text=${shareText}&url=${shareUrl}`;
      shareBtn.target = '_blank';
      shareBtn.rel = 'noopener noreferrer';
      shareBtn.className = 'inline-flex items-center gap-2 bg-[#1DA1F2]/10 hover:bg-[#1DA1F2] text-[#1DA1F2] hover:text-white text-xs font-black px-4 py-2.5 rounded-xl transition-all duration-300 cursor-pointer border border-[#1DA1F2]/30 shadow-lg uppercase tracking-wider group';
      
      shareBtn.innerHTML = `
        <svg class="w-4 h-4 group-hover:scale-110 transition-transform" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
        <span>Tweetar Citação</span>
      `;

      bq.appendChild(btnContainer);
      btnContainer.appendChild(shareBtn);
      
      // Ícone de aspas duplo (Premium Detail) flutuante
      const quoteIcon = document.createElement('div');
      quoteIcon.className = 'absolute -top-5 -left-5 w-10 h-10 bg-theme-accent text-white rounded-full flex items-center justify-center font-serif text-4xl shadow-[0_0_15px_rgba(var(--theme-accent-rgb),0.5)] pt-3 opacity-90';
      quoteIcon.innerHTML = '“';
      bq.appendChild(quoteIcon);
    });
  }, []);

  return null;
}
