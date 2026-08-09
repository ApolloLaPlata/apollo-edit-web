import Link from 'next/link';
import React from 'react';
import db from '@/lib/db';
import { Metadata } from 'next';
import ExitIntentPopup from '@/components/blog/ExitIntentPopup';
import ScrollToTop from '@/components/blog/ScrollToTop';
import WebPushBanner from '@/components/blog/WebPushBanner';
import LayoutRouter from '@/components/blog/templates/LayoutRouter';
import FloatingPagination from '@/components/blog/FloatingPagination';
import type { PostData, CategoryData, BlogData } from '@/components/blog/templates/LayoutRouter';

export async function generateMetadata(props: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const params = await props.params;
  const rawDomain = decodeURIComponent(params.domain);
  const decodedDomain = rawDomain.split(':')[0];
  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  if (!blogMeta) return { title: 'Blog não encontrado' };

  const description = `As últimas notícias, análises e tendências publicadas pelo ${blogMeta.name}.`;
  const baseUrl = `https://${decodedDomain}`;

  return {
    title: `${blogMeta.name} | Notícias em Tempo Real`,
    description,
    metadataBase: new URL(baseUrl),
    alternates: {
      canonical: baseUrl,
      types: { 'application/rss+xml': `${baseUrl}/rss.xml` }
    },
    openGraph: {
      title: blogMeta.name,
      description,
      url: baseUrl,
      siteName: blogMeta.name,
      images: [{
        url: `https://${decodedDomain}/api/og?title=${encodeURIComponent('Página Inicial')}&siteName=${encodeURIComponent(blogMeta.name)}`,
        width: 1200,
        height: 630,
        alt: blogMeta.name
      }],
      type: 'website',
      locale: 'pt_BR',
    },
    twitter: {
      card: 'summary_large_image',
      title: blogMeta.name,
      description,
      images: [`https://${decodedDomain}/api/og?title=${encodeURIComponent('Página Inicial')}&siteName=${encodeURIComponent(blogMeta.name)}`],
    },
    robots: { index: true, follow: true }
  };
}

export default async function Home(props: {
  params: Promise<{ domain: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const rawDomain = decodeURIComponent(params.domain);
  const decodedDomain = rawDomain.split(':')[0]; // Remove porta :3000 se existir
  const lang = (typeof searchParams.lang === 'string') ? searchParams.lang : 'pt';

  // ─── Carregar dados do blog ───────────────────────────────
  let blogRaw = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogRaw && decodedDomain.includes('localhost')) {
    blogRaw = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }

  const blog: BlogData = {
    id: String(blogRaw?.id || ''),
    name: blogRaw?.name || 'Portal',
    domain: decodedDomain,
    niche: blogRaw?.niche || 'Geral',
    description: blogRaw?.description || '',
    theme: blogRaw?.theme || 'dark',
    primaryColor: blogRaw?.primaryColor || '#06b6d4',
    secondaryColor: blogRaw?.secondaryColor || '#3b82f6',
    layoutStyle: blogRaw?.layoutStyle || 'classic_portal',
    fontFamily: blogRaw?.fontFamily || 'inter',
    logoUrl: blogRaw?.logoUrl || '',
    accentStyle: blogRaw?.accentStyle || 'rounded',
  };

  // ─── Paginação (Server-Side) ──────────────────────────────
  const pageStr = (typeof searchParams.page === 'string') ? searchParams.page : '1';
  const currentPage = Math.max(1, parseInt(pageStr, 10) || 1);
  const postsPerPage = 6;
  const offset = (currentPage - 1) * postsPerPage;

  // Busca posts + 1 (para saber se existe próxima página)
  const recentPostsRaw = db.prepare(`
    SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
    FROM Post
    LEFT JOIN Blog ON Post.blogId = Blog.id
    WHERE Post.blogId = ? AND Post.language = ? AND Post.isPublished = 1
    ORDER BY Post.createdAt DESC LIMIT ? OFFSET ?
  `).all(blogRaw?.id, lang, postsPerPage + 1, offset) as any[];

  const hasNextPage = recentPostsRaw.length > postsPerPage;
  const postsToRender = recentPostsRaw.slice(0, postsPerPage);

  const recentPosts: PostData[] = postsToRender.map((p: any) => ({
    id: String(p.id),
    title: p.title,
    slug: p.slug,
    contentMd: p.contentMd || '',
    coverImage: p.coverImage || '',
    author: (p.author || '').replace(/Redação IA/gi, p.blog_name || 'Redação Especial') || p.blog_name || 'Redação',
    createdAt: p.createdAt,
    category: p.category || '',
    blog: { name: p.blog_name, domain: p.blog_domain },
  }));

  // ─── Buscar Web Stories (Posts com videoUrl) ────────────────
  const webStoriesRaw = db.prepare(`
    SELECT id, title, slug, coverImage, videoUrl, blogId
    FROM Post
    WHERE blogId = ? AND isPublished = 1 AND videoUrl IS NOT NULL
    ORDER BY createdAt DESC LIMIT 10
  `).all(blogRaw?.id) as any[];

  const webStories = webStoriesRaw.map((s: any) => ({
    id: String(s.id),
    title: s.title,
    slug: s.slug,
    coverImage: s.coverImage || '',
    videoUrl: s.videoUrl,
    blogName: blog.name
  }));

  // Se estivermos na página 1, o primeiro post é o Hero. 
  // Se for página > 1, não há hero, e os 6 posts caem direto no grid.
  const heroPost: PostData | null = currentPage === 1 ? (recentPosts[0] || null) : null;
  const otherPosts: PostData[] = currentPage === 1 ? recentPosts.slice(1) : recentPosts;

  // ─── Carregar categorias ──────────────────────────────────
  const categoriesRaw = db.prepare(
    'SELECT name, slug FROM Category WHERE blogId = ? LIMIT 8'
  ).all(blogRaw?.id) as any[];

  const categories: CategoryData[] = categoriesRaw.map((c: any) => ({
    name: c.name,
    slug: c.slug,
  }));

  return (
    <>
      {/* Schema JSON-LD (SEO — igual em todos os templates) */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            '@context': 'https://schema.org',
            '@type': 'WebSite',
            'url': `https://${decodedDomain}`,
            'name': blog.name,
            'potentialAction': {
              '@type': 'SearchAction',
              'target': {
                '@type': 'EntryPoint',
                'urlTemplate': `https://${decodedDomain}/?lang=${lang}&q={search_term_string}`
              },
              'query-input': 'required name=search_term_string'
            }
          })
        }}
      />

      {/* ── ROTEADOR DE TEMPLATES ── */}
      {/* Todos os templates recebem os mesmos dados. */}
      {/* O layoutStyle salvo no SQLite determina qual template renderizar. */}
      <LayoutRouter
        blog={blog}
        heroPost={heroPost}
        otherPosts={otherPosts}
        webStories={webStories}
        categories={categories}
        lang={lang}
        domain={decodedDomain}
      />

      <div style={{ padding: '4rem 2rem', textAlign: 'center', backgroundColor: '#0a0a0a' }}>
        <a 
          href="https://apolloedit.com.br/" 
          style={{ display: 'inline-block', padding: '1.5rem 3rem', backgroundColor: '#06b6d4', color: '#fff', fontSize: '1.5rem', fontWeight: 'bold', borderRadius: '1rem', textDecoration: 'none', boxShadow: '0 4px 14px 0 rgba(6, 182, 212, 0.39)' }}
        >
          Acessar o Apollo Edit Oficial
        </a>
      </div>

      <FloatingPagination currentPage={currentPage} hasNextPage={hasNextPage} lang={lang} />
      <ExitIntentPopup blogId={String(blog.id)} />
      <WebPushBanner />
      <ScrollToTop />
    </>
  );
}
