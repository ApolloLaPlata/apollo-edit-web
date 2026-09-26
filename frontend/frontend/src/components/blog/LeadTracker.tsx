'use client';
import { useEffect } from 'react';

export default function LeadTracker({ domain, blogId }: { domain: string, blogId: string }) {
  useEffect(() => {
    // Evita rodar no SSR
    if (typeof window === 'undefined') return;

    const trackLead = async () => {
      try {
        // Gerador de Fingerprint simples (Multi-tenant Tracking)
        const getFingerprint = () => {
          const nav = window.navigator;
          const screen = window.screen;
          const guid = nav.userAgent + screen.height + screen.width + nav.language;
          
          let hash = 0;
          for (let i = 0; i < guid.length; i++) {
            const char = guid.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
          }
          return Math.abs(hash).toString(16);
        };

        const fingerprint = getFingerprint();
        
        // Pega Cookie de Lead Global (se existir)
        const leadCookie = document.cookie.split('; ').find(row => row.startsWith('apollo_lead_id='));
        const leadId = leadCookie ? leadCookie.split('=')[1] : fingerprint;

        // Atualiza Cookie para persistir o Lead
        document.cookie = `apollo_lead_id=${leadId}; path=/; max-age=31536000; SameSite=Lax`;

        // Aqui enviaríamos para o Hub Central do Maestro
        // Exemplo: fetch('https://hub.apolloedit.com/api/track', { ... })
        // Como estamos simulando a fundação:
        
        console.log(`📡 [APOLLO HUB] Lead Retargeting Tracked: ${leadId} no domínio ${domain}`);

        // Opcional: Se já visitou outro blog da rede (cookie global via iframe cross-domain na versão PRO),
        // poderíamos injetar Ads personalizados agora.

      } catch (e) {
        // Tracker silencioso não deve gerar erros visuais
      }
    };

    // Atraso intencional para não bloquear TTI (Time to Interactive)
    const timer = setTimeout(trackLead, 1500);
    return () => clearTimeout(timer);
  }, [domain, blogId]);

  return null; // Componente Invisível
}
