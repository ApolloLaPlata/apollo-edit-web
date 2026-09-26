import React from 'react';
import SynapseClient from './SynapseClient';

export const metadata = {
  title: '🕸️ Sistema Nervoso & Sinapses de SEO | Apollo Auto-Blog CMS',
  description: 'Acompanhe a teia neural de links internos, otimização A/B de títulos e disparos virais no Megafone em tempo real.',
};

export default function SynapsesPage() {
  return <SynapseClient />;
}
