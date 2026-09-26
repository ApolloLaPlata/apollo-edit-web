import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { ReactNode } from 'react';
import ReadStatusEnforcer from '@/components/blog/ReadStatusEnforcer';
import MobileBottomNav from '@/components/blog/MobileBottomNav';
import LeadTracker from '@/components/blog/LeadTracker';

import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const { domain } = await params;
  const decodedDomain = decodeURIComponent(domain);
  
  const blog = await db.prepare('SELECT name, description, niche, logoUrl FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog) return { title: 'Site Not Found' };

  return {
    title: {
      template: `%s | ${blog.name}`,
      default: blog.name,
    },
    description: blog.description || `O melhor conteúdo sobre ${blog.niche}`,
    openGraph: {
      title: blog.name,
      description: blog.description || `O melhor conteúdo sobre ${blog.niche}`,
      siteName: blog.name,
      images: blog.logoUrl ? [{ url: blog.logoUrl }] : [],
    },
    twitter: {
      card: 'summary_large_image',
      title: blog.name,
      description: blog.description,
    },
    alternates: {
      canonical: `https://${decodedDomain}`,
    }
  };
}

export default async function DomainLayout({
  children,
  params
}: {
  children: ReactNode;
  params: Promise<{ domain: string }>;
}) {
  const { domain } = await params;
  
  // Decodifica o domínio
  const decodedDomain = decodeURIComponent(domain);
  
  // Busca as configurações visuais avançadas do Blog
  const blog = await db.prepare('SELECT primaryColor, secondaryColor, layoutStyle, bgPrimary, bgSurface, fontHeading, fontBody, bannerUrl FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  
  if (!blog) {
    return children; // Falldown para layout padrão se não achar
  }

  // Fallbacks de cores caso estejam vazias
  const primary = blog.primaryColor || '#3b82f6';
  const secondary = blog.secondaryColor || '#1e40af';
  const bgPrimary = blog.bgPrimary || '#020617';
  const bgSurface = blog.bgSurface || '#1e293b';
  const fontHeading = blog.fontHeading || 'Inter';
  const fontBody = blog.fontBody || 'Inter';
  const bannerUrl = blog.bannerUrl || '';

  // Processa nomes das fontes para a URL do Google Fonts
  const fontQuery = Array.from(new Set([fontHeading, fontBody]))
    .map(font => `family=${font.replace(/ /g, '+')}:wght@400;500;700;900`)
    .join('&');

  return (
    <>
      <style dangerouslySetInnerHTML={{
        __html: `
          @import url('https://fonts.googleapis.com/css2?${fontQuery}&display=swap');
          
          :root {
            --accent: ${primary};
            --accent-hover: ${primary}dd;
            --bg-primary: ${bgPrimary};
            --bg-surface: ${bgSurface};
            --font-heading: '${fontHeading}', sans-serif;
            --font-body: '${fontBody}', sans-serif;
          }

          body {
            background-color: var(--bg-primary);
            font-family: var(--font-body);
            ${bannerUrl ? `background-image: linear-gradient(to bottom, var(--bg-primary) 0%, transparent 100%), url('${bannerUrl}'); background-size: 100% 450px; background-repeat: no-repeat; background-position: top center;` : ''}
          }

          h1, h2, h3, h4, h5, h6, .font-heading {
            font-family: var(--font-heading) !important;
          }
        `
      }} />
      <div className={`theme-${blog.layoutStyle || 'magazine'}`}>
        <LeadTracker domain={decodedDomain} blogId={blog.id} />
        <ReadStatusEnforcer />
        {children}
        <MobileBottomNav domain={decodedDomain} />
      </div>
    </>
  );
}
