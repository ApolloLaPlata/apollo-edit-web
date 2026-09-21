import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import NavbarMaster from '@/components/ui/NavbarMaster';

export async function generateMetadata(props: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const blog = db.prepare('SELECT name FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  return { title: `Oferta Exclusiva | ${blog?.name || decodedDomain}`, robots: { index: false, follow: false } };
}

export default async function OfertasPage(props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  
  const blog = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog && !decodedDomain.includes('localhost')) {
    notFound();
  }

  return (
    <div className={`min-h-screen bg-slate-50 text-slate-900 font-sans`}>
      {/* Navbar simplificada para não distrair (Landing Page Style) */}
      <div className="bg-black text-white text-center py-4 font-black uppercase tracking-widest">
         Advertorial - Informação Comercial
      </div>
      
      <main className="max-w-3xl mx-auto px-4 py-8">
        <h1 className="text-3xl md:text-5xl font-black tracking-tighter mb-6 text-center text-red-600 leading-tight">
          Médicos Chocados: O "Truque de 2 Minutos" Antes de Dormir Que Seca a Barriga Naturalmente
        </h1>
        
        <div className="flex items-center justify-center gap-4 mb-8 text-sm font-bold text-slate-500 uppercase tracking-widest">
           <span>Atualizado Hoje</span>
           <span>•</span>
           <span>Patrocinado</span>
        </div>

        <div className="w-full aspect-video bg-black rounded-2xl flex items-center justify-center mb-8 shadow-2xl relative overflow-hidden group">
           {/* Falso Vídeo VSL */}
           <img src="https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=1200&q=80" alt="Médico" className="absolute inset-0 w-full h-full object-cover opacity-60" />
           <div className="w-20 h-20 bg-red-600 rounded-full flex items-center justify-center text-white text-3xl shadow-xl z-10 cursor-pointer group-hover:scale-110 transition-transform animate-pulse">
              ▶
           </div>
        </div>
        
        <div className="prose prose-lg max-w-none text-slate-800 space-y-6">
          <p className="lead font-bold text-xl">
            Uma descoberta recente em uma universidade americana revelou que a dificuldade de perder peso após os 40 anos não tem a ver com metabolismo lento, mas sim com uma falha noturna durante o sono.
          </p>
          <p>
            Milhares de homens e mulheres estão utilizando um método simples e natural de 2 minutos antes de ir para a cama. Esse processo desativa o acúmulo de gordura e restaura as funções vitais...
          </p>

          <div className="bg-yellow-100 border-l-4 border-yellow-500 p-6 my-8">
             <h3 className="font-black text-xl mb-2">Atenção: Oferta Limitada</h3>
             <p>O vídeo de apresentação deste método pode sair do ar a qualquer momento devido à pressão da indústria farmacêutica.</p>
          </div>

          <a href="https://example.com/seu-link-de-afiliado-aqui" target="_blank" rel="noopener noreferrer" className="block w-full bg-green-600 hover:bg-green-500 text-white font-black text-2xl uppercase tracking-widest py-6 px-8 rounded-2xl text-center shadow-[0_10px_30px_rgba(22,163,74,0.4)] transition-transform hover:-translate-y-2">
             Assistir Apresentação Oficial ↗
          </a>
        </div>
      </main>
    </div>
  );
}
