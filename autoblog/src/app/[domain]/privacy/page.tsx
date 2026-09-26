import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import NavbarMaster from '@/components/ui/NavbarMaster';
import Footer from '@/components/blog/Footer';

export async function generateMetadata(props: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const blog = await db.prepare('SELECT name FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  return { title: `Política de Privacidade | ${blog?.name || decodedDomain}`, robots: { index: false, follow: true } };
}

export default async function PrivacyPolicyPage(props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  
  const blog = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog && !decodedDomain.includes('localhost')) {
    notFound();
  }

  const siteName = blog?.name || 'Nosso Portal';

  return (
    <div className={`min-h-screen bg-theme-bg text-theme-text font-sans`}>
      <NavbarMaster blog={blog || {}} categories={[]} lang="pt" domain={decodedDomain} />
      
      <main className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-black uppercase tracking-tighter mb-8">Política de Privacidade</h1>
        
        <div className="prose prose-invert max-w-none text-slate-300 space-y-6">
          <p>
            Esta Política de Privacidade descreve como o <strong>{siteName}</strong> coleta, usa e protege as 
            informações pessoais que você nos fornece. Ao usar nossos serviços, você concorda com o uso de seus dados 
            conforme estipulado nesta política, em conformidade com as leis de proteção de dados.
          </p>
          
          <h2 className="text-2xl font-bold text-white mt-8">1. Coleta de Dados</h2>
          <p>
            Coletamos informações que você fornece ativamente (como e-mail ao assinar a newsletter) 
            e dados automáticos (cookies, endereço de IP, navegador) para melhorar a performance.
          </p>

          <h2 className="text-2xl font-bold text-white mt-8">2. Uso e Compartilhamento</h2>
          <p>
            Não vendemos seus dados para terceiros. Compartilhamos anonimamente com parceiros de publicidade (ex: Google AdSense) estritamente para segurança e exibição de mídia relevante.
          </p>
        </div>
      </main>
      <Footer domain={decodedDomain} name={blog?.name} />
    </div>
  );
}
