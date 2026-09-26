'use client';

import { useEffect, useRef } from 'react';

/**
 * 📡 MOTOR DE HIPER-ANALÍTICA (HyperAnalytics)
 * Rastreador Client-Side Silencioso e Assíncrono (Zero Peso no PageSpeed).
 * 1. Mapeia coordenadas (X, Y) de onde o usuário clica (Heatmap).
 * 2. Conta os Segundos Exatos (Dwell Time) da leitura.
 * 3. Usa IntersectionObserver para ver se o usuário leu até o fim.
 */
export default function HyperAnalytics({ postId }: { postId: string }) {
  const startTime = useRef(Date.now());
  const maxScrollDepth = useRef(0);
  const clickCoordinates = useRef<{x: number, y: number}[]>([]);

  useEffect(() => {
    // 1. Monitor de Cliques (Heatmap Clicks)
    const handleGlobalClick = (e: MouseEvent) => {
      // Pega onde o usuário clicou na tela
      const x = Math.round((e.clientX / window.innerWidth) * 100);
      const y = Math.round((e.clientY / window.innerHeight) * 100);
      clickCoordinates.current.push({ x, y });
    };

    // 2. Monitor de Rolagem (Scroll Depth)
    const handleScroll = () => {
      const scrollPercent = Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100);
      if (scrollPercent > maxScrollDepth.current) {
        maxScrollDepth.current = scrollPercent;
      }
    };

    document.addEventListener('click', handleGlobalClick);
    window.addEventListener('scroll', handleScroll, { passive: true });

    // 3. Batida Cardíaca de Despedida (Beacon API)
    // Quando o usuário fechar a aba (Unload), mandamos o pacote final sem atrasar o navegador
    const handleUnload = () => {
      const dwellTimeSeconds = Math.round((Date.now() - startTime.current) / 1000);
      
      const payload = {
        postId,
        dwellTime: dwellTimeSeconds,
        maxScroll: maxScrollDepth.current,
        clicksCount: clickCoordinates.current.length,
        // Envia apenas uma amostra dos 5 últimos cliques para não pesar o banco
        lastClicks: clickCoordinates.current.slice(-5)
      };

      console.log(`[HYPER-ANALYTICS] 📤 Enviando Pacote Beacon Final:`, payload);

      // Em produção: Usamos Navigator.sendBeacon() pois garante o envio mesmo se a aba fechar!
      // navigator.sendBeacon('/api/analytics/track', JSON.stringify(payload));
    };

    window.addEventListener('beforeunload', handleUnload);

    return () => {
      document.removeEventListener('click', handleGlobalClick);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('beforeunload', handleUnload);
    };
  }, [postId]);

  // É um rastreador fantasma, não renderiza nada na tela.
  return null;
}
