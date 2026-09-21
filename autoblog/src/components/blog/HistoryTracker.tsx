'use client';

import { useEffect } from 'react';

interface HistoryTrackerProps {
  domain: string;
  slug: string;
  title: string;
}

export default function HistoryTracker({ domain, slug, title }: HistoryTrackerProps) {
  useEffect(() => {
    try {
      const stored = localStorage.getItem('reading_history');
      let history = stored ? JSON.parse(stored) : [];
      
      // Remove se já existir para colocar no topo
      history = history.filter((item: any) => item.slug !== slug);
      
      // Adiciona no topo
      history.unshift({
        domain,
        slug,
        title,
        timestamp: Date.now()
      });

      // Limita a 20 registros globais para não pesar no LocalStorage
      if (history.length > 20) {
        history = history.slice(0, 20);
      }

      localStorage.setItem('reading_history', JSON.stringify(history));
    } catch (e) {
      console.error('Erro ao salvar histórico', e);
    }
  }, [domain, slug, title]);

  return null;
}
