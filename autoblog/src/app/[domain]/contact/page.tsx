import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import NavbarMaster from '@/components/ui/NavbarMaster';
import Footer from '@/components/blog/Footer';
import ContactForm from '@/components/blog/ContactForm';

export async function generateMetadata(props: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const blog = db.prepare('SELECT name FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  return { title: `Contato Editorial | ${blog?.name || decodedDomain}`, robots: { index: true, follow: true } };
}

export default async function ContactPage(props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  
  const blog = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog && !decodedDomain.includes('localhost')) {
    notFound();
  }

  return (
    <div className={`min-h-screen bg-theme-bg text-theme-text font-sans`}>
      <NavbarMaster blog={blog || {}} categories={[]} lang="pt" domain={decodedDomain} />
      
      <main className="max-w-4xl mx-auto px-4 py-16">
        <h1 className="text-4xl font-black uppercase tracking-tighter mb-8">Fale Conosco</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          <div className="space-y-6">
             <p className="text-slate-300">
               O canal de contato da redação do <strong>{blog?.name}</strong> está aberto para envios de pautas, propostas comerciais ou comunicação de correções de informações.
             </p>
             
             <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
                <h3 className="text-sm uppercase tracking-widest font-black text-theme-accent mb-2">E-mail Corporativo</h3>
                <p className="font-mono text-lg text-white">redacao@{decodedDomain}</p>
             </div>
          </div>
          
          <ContactForm domain={decodedDomain} />
        </div>
      </main>

      <Footer domain={decodedDomain} name={blog?.name} />
    </div>
  );
}
