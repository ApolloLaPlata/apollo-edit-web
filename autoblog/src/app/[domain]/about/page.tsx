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
  return { title: `Sobre Nós | ${blog?.name || decodedDomain}`, robots: { index: true, follow: true } };
}

export default async function AboutPage(props: { params: Promise<{ domain: string }> }) {
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
        <h1 className="text-4xl font-black uppercase tracking-tighter mb-8">Sobre a Nossa Redação</h1>
        
        <div className="prose prose-invert max-w-none text-slate-300 space-y-6">
          <p>
            O <strong>{siteName}</strong> é um veículo independente fundado sob os mais estritos princípios do jornalismo de dados e da informação em tempo real.
          </p>
          
          <h2 className="text-2xl font-bold text-white mt-8">Nossa Missão</h2>
          <p>
            Democratizar o acesso à informação rápida e precisa, utilizando as mais modernas tecnologias de compilação e redação para trazer as tendências de {blog?.niche || 'conteúdo'} diretamente para a tela do leitor sem atrasos.
          </p>

          <h2 className="text-2xl font-bold text-white mt-8">Nossa Equipe</h2>
          <p>
            Contamos com uma estrutura de engenharia de dados (Desk Analytics) que nos permite fazer o cruzamento global de tendências, entregando matérias apuradas, revisadas e ágeis 24 horas por dia.
          </p>
        </div>
      </main>
      <Footer domain={decodedDomain} name={blog?.name} />
    </div>
  );
}
