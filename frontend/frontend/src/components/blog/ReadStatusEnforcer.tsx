'use client';
import { useEffect } from 'react';

export default function ReadStatusEnforcer() {
  useEffect(() => {
    try {
      const stored = localStorage.getItem('reading_history');
      if (!stored) return;
      
      const history = JSON.parse(stored);
      if (!Array.isArray(history) || history.length === 0) return;

      // Cria um mapa rápido de slugs lidos
      const readSlugs = new Set(history.map(item => item.slug));

      // Busca todos os links de posts na tela (supondo que o link contém /blog/slug)
      const allLinks = document.querySelectorAll('a[href*="/blog/"]');

      allLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (!href) return;
        
        // Tenta extrair o slug da URL
        const parts = href.split('/blog/');
        if (parts.length > 1) {
          const slug = parts[1].replace(/\/$/, ''); // Remove trailing slash
          
          if (readSlugs.has(slug)) {
            // Se o link é um card (contém filhos grandes), escurecemos o card.
            // Se for apenas texto (ex: sidebar), escurecemos o texto.
            link.classList.add('post-read');
            
            // Tenta achar um container de card pra aplicar a classe também
            const cardParent = link.closest('.glass-card, .group');
            if (cardParent) {
              cardParent.classList.add('post-read-card');
            }
          }
        }
      });
    } catch (e) {
      console.error('Erro ao processar status de leitura', e);
    }
  }, []);

  return null;
}
