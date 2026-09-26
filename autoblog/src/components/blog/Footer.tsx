import Link from 'next/link';
import React from 'react';
import db from '@/lib/db';
import SocialConnectBar from './SocialConnectBar';

interface FooterProps {
  domain?: string;
  name?: string;
  blogName?: string;
}

export default async function Footer({ domain = '', name, blogName }: FooterProps) {
  const siteName = name || blogName || 'Portal Colmeia';
  let blogMeta = await db.prepare('SELECT socialLinks, primaryColor FROM Blog WHERE domain = ?').get(domain) as any;
  if (!blogMeta && (domain.includes('localhost') || !domain)) {
    blogMeta = await db.prepare('SELECT socialLinks, primaryColor FROM Blog LIMIT 1').get() as any;
  }

  return (
    <>
      <SocialConnectBar 
        socialLinksRaw={blogMeta?.socialLinks} 
        primaryColor={blogMeta?.primaryColor || '#3b82f6'} 
        siteName={siteName} 
      />
      <footer className="w-full border-t border-theme-border bg-theme-surface mt-auto py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8 border-b border-theme-border/50 pb-8">
          
          {/* Logo e Intro */}
          <div className="col-span-1">
            <Link href={`/`} className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 bg-theme-accent rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-theme-text font-black font-serif text-lg">{siteName.charAt(0) || "O"}</span>
              </div>
              <span className="font-black text-2xl tracking-tight text-theme-text uppercase">
                {siteName}
              </span>
            </Link>
            <p className="text-theme-muted text-sm leading-relaxed max-w-xs font-medium">
              O seu portal diário para conteúdo gerado com precisão analítica e inteligência artificial de ponta.
            </p>
          </div>

          {/* Navegação */}
          <div className="col-span-1">
            <h4 className="text-theme-text font-black uppercase tracking-widest text-xs mb-4">Explore</h4>
            <ul className="space-y-3">
              <li>
                <Link href={`/`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  Página Inicial
                </Link>
              </li>
              <li>
                <Link href={`/?lang=en`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  English Version
                </Link>
              </li>
              <li>
                <Link href={`/?lang=es`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  Versión en Español
                </Link>
              </li>
            </ul>
          </div>

          {/* Institucional (AdSense Compliance) */}
          <div className="col-span-1">
            <h4 className="text-theme-text font-black uppercase tracking-widest text-xs mb-4">Institucional</h4>
            <ul className="space-y-3">
              <li>
                <Link href={`/p/sobre-nos`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  Sobre Nós
                </Link>
              </li>
              <li>
                <Link href={`/p/politica-de-privacidade`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  Política de Privacidade
                </Link>
              </li>
              <li>
                <Link href={`/p/termos-de-uso`} className="text-sm text-theme-muted hover:text-theme-accent transition-colors font-semibold">
                  Termos de Uso
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center text-xs text-theme-muted font-medium">
          <p>© {new Date().getFullYear()} {siteName}. Todos os direitos reservados.</p>
          <p className="mt-2 md:mt-0 flex items-center gap-1">
            Desenvolvido com <span className="text-red-500">❤️</span> e IA
          </p>
        </div>
      </div>
    </footer>
    </>
  );
}
