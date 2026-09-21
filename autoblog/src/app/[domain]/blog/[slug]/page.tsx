import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import rehypeRaw from 'rehype-raw';
import rehypeStringify from 'rehype-stringify';
import rehypeSlug from 'rehype-slug';
import DOMPurify from 'isomorphic-dompurify';
import dynamic from 'next/dynamic';
import PodcastPlayer from './PodcastPlayer';
import AdBanner from '@/components/blog/AdBanner';
import RelatedPosts from '@/components/blog/RelatedPosts';
import NewsTicker from '@/components/blog/NewsTicker';
import ViewTracker from '@/components/blog/ViewTracker';
import PaywallBlocker from '@/components/blog/PaywallBlocker';
import SearchBar from '@/components/blog/SearchBar';
import TableOfContents from '@/components/blog/TableOfContents';
import FloatingShare from '@/components/blog/FloatingShare';
import ScrollToTop from '@/components/blog/ScrollToTop';
import ZenModeToggle from '@/components/blog/ZenModeToggle';
import ParallaxCover from '@/components/blog/ParallaxCover';
import ArticleComments from '@/components/blog/ArticleComments';
import ImageLightbox from '@/components/blog/ImageLightbox';
import SensitiveContentBlocker from '@/components/blog/SensitiveContentBlocker';
import ArticleTLDR from '@/components/blog/ArticleTLDR';
import FloatingReadMore from '@/components/blog/FloatingReadMore';
import InteractiveBlockquotes from '@/components/blog/InteractiveBlockquotes';
import TextToSpeechPlayer from '@/components/blog/TextToSpeechPlayer';
const ArticleReactions = dynamic(() => import('@/components/blog/ArticleReactions'), { loading: () => <div className="h-20 w-full animate-pulse bg-slate-800/20 rounded-xl" /> });
import ArticleChatbot from '@/components/blog/ArticleChatbot';
import ExitIntentPopup from '@/components/blog/ExitIntentPopup';
import HistoryTracker from '@/components/blog/HistoryTracker';
import MobileStickyAd from '@/components/blog/MobileStickyAd';
import ReadingHistory from '@/components/blog/ReadingHistory';
import NewsletterWidget from '@/components/blog/NewsletterWidget';
import DonationTipJar from '@/components/blog/DonationTipJar';
import NavbarMaster from '@/components/ui/NavbarMaster';
import Footer from '@/components/blog/Footer';
import InteractiveMediaRouter from '@/components/blog/interactive/InteractiveMediaRouter';
import ReadingProgress from '@/components/blog/ReadingProgress';
import ChatGPTBait from '@/components/blog/ChatGPTBait';

// Função utilitária para limpar excertos
function cleanExcerpt(markdown: string) {
  return markdown
    .replace(/[#*`_\[\]>!]/g, '')
    .replace(/={3,}/g, '')
    .replace(/-/g, '')
    .replace(/Este é um artigo gerado automaticamente.*?\./gi, '')
    .replace(/Não posso atender a esta solicitação.*?\./gi, '')
    .replace(/\s+/g, ' ')
    .trim();
}

export const revalidate = 3600; // FASE 2: Caching Severo (Regerado a cada 1 hora)

export async function generateMetadata(props: { params: Promise<{ domain: string, slug: string }> }): Promise<Metadata> {
  const params = await props.params;
  const rawDomain = decodeURIComponent(params.domain);
  const decodedDomain = rawDomain.split(':')[0];
  const slug = decodeURIComponent(params.slug);

  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const postRaw = db.prepare(`SELECT title, contentMd, coverImage FROM Post WHERE slug = ? AND blogId = ?`).get(slug, blogMeta?.id) as any;
  
  if (!postRaw) return { title: 'Artigo não encontrado' };

  // Gera uma descrição de 160 chars limpando markdown
  const description = cleanExcerpt(postRaw.contentMd).substring(0, 160) + '...';
  const canonicalUrl = `https://${decodedDomain}/blog/${slug}`;
  const siteName = blogMeta?.name || decodedDomain;

  return {
    title: `${postRaw.title} | ${siteName}`,
    description,
    metadataBase: new URL(`https://${decodedDomain}`),
    alternates: { 
      canonical: canonicalUrl,
      types: {
        'application/rss+xml': `https://${decodedDomain}/rss.xml`
      }
    },
    keywords: [postRaw.title.split(' ').join(', '), 'notícias', 'análise', siteName],
    openGraph: {
      title: postRaw.title,
      description,
      url: canonicalUrl,
      siteName,
      images: [
        { 
          url: postRaw.coverImage ? postRaw.coverImage : `https://${decodedDomain}/api/og?title=${encodeURIComponent(postRaw.title)}&siteName=${encodeURIComponent(siteName)}`, 
          width: 1200, 
          height: 630, 
          alt: postRaw.title 
        }
      ],
      type: 'article',
      locale: 'pt_BR',
    },
    twitter: {
      card: 'summary_large_image',
      title: postRaw.title,
      description,
      images: [postRaw.coverImage ? postRaw.coverImage : `https://${decodedDomain}/api/og?title=${encodeURIComponent(postRaw.title)}&siteName=${encodeURIComponent(siteName)}`],
    },
    robots: { index: true, follow: true }
  };
}

export default async function BlogPost(
  props: { params: Promise<{ domain: string, slug: string }>, searchParams: Promise<{ [key: string]: string | string[] | undefined }> }
) {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);
  const lang = (typeof searchParams.lang === 'string') ? searchParams.lang : 'pt';

  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';

  const postRaw = db.prepare(`
    SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
    FROM Post 
    LEFT JOIN Blog ON Post.blogId = Blog.id 
    WHERE Post.slug = ? AND Post.blogId = ?
  `).get(slug, blogMeta?.id) as any;

  if (!postRaw) {
    notFound();
  }

  const post = {
    ...postRaw,
    author: (postRaw.author || '').replace(/Redação IA/gi, postRaw.blog_name || 'Redação Especial') || postRaw.blog_name || 'Redação',
    blog: { name: postRaw.blog_name, domain: postRaw.blog_domain }
  };

  // Pegar recentes para o Ticker
  const recentPosts = db.prepare(`SELECT * FROM Post LIMIT 5`).all();
  const otherPosts = db.prepare(`SELECT * FROM Post WHERE id != ? LIMIT 4`).all(post.id) as any[];

  const categories = db.prepare(`SELECT name, slug FROM Category WHERE blogId = ? LIMIT 4`).all(blogMeta?.id) as any[];

  // Pegar Categoria do Post Atual
  const postCategory = db.prepare(`
    SELECT Category.name 
    FROM Category 
    JOIN PostCategory ON Category.id = PostCategory.categoryId 
    WHERE PostCategory.postId = ?
  `).get(post.id) as any;

  // Pegar Comentários Fantasmas
  const comments = db.prepare(`SELECT * FROM Comment WHERE postId = ? ORDER BY createdAt ASC`).all(post.id) as any[];

  // Extração do Resumo IA (TLDR)
  const tldrRegex = /\[TLDR\]([\s\S]*?)\[\/TLDR\]/i;
  const tldrMatch = post.contentMd.match(tldrRegex);
  const tldrContent = tldrMatch ? tldrMatch[1] : null;

  // Verificação de Sensibilidade da IA
  const isSensitive = post.contentMd.includes('[SENSITIVE]');
  
  // Limpeza de Tags Internas antes do Parser do Markdown
  let cleanMdForParsing = post.contentMd.replace(/\[SENSITIVE\]/gi, '');
  if (tldrContent) {
    cleanMdForParsing = cleanMdForParsing.replace(tldrRegex, '');
  }

  // ANCORAGEM AUTOMÁTICA DE AFILIADOS (In-Text Monetization)
  let affiliateOffer: any = null;
  try {
    // A tabela AffiliateLink (Fase 115) é global na Máfia
    const affiliateLinks = db.prepare('SELECT keyword, url FROM AffiliateLink WHERE isActive = 1').all() as any[];
    if (affiliateLinks && affiliateLinks.length > 0) {
      // Pega uma oferta aleatória para o Highlight Box
      affiliateOffer = affiliateLinks[Math.floor(Math.random() * affiliateLinks.length)];
      
      affiliateLinks.forEach(offer => {
        if (offer.keyword && offer.url) {
          // Lookbehind/lookahead para evitar substituir dentro de atributos HTML ou URLs
          const regex = new RegExp(`(?<![<\\/\\[\\-])\\b(${offer.keyword})\\b(?![>\\/\\]\\-])`, 'gi');
          cleanMdForParsing = cleanMdForParsing.replace(regex, `<a href="${offer.url}" target="_blank" rel="sponsored noopener" class="text-theme-accent font-extrabold px-1 rounded bg-theme-accent/10 border-b-2 border-theme-accent/40 hover:bg-theme-accent/20 transition-all inline-flex items-center gap-1">$1<svg class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg></a>`);
        }
      });
    }
  } catch (e) {
    console.error("Erro na injeção de afiliados:", e);
  }

  // FASE 108: AUTO-LINKAGEM INTERNA (PROGRAMMATIC SEO)
  try {
    // Busca até 10 outros posts recentes do mesmo blog para fazer cross-link
    const allBlogPosts = db.prepare('SELECT title, slug FROM Post WHERE blogId = ? AND id != ? ORDER BY createdAt DESC LIMIT 10').all(blogMeta?.id, post.id) as any[];
    
    if (allBlogPosts && allBlogPosts.length > 0) {
      allBlogPosts.forEach(targetPost => {
        // Tenta pegar uma palavra-chave relevante do título (acima de 5 letras)
        const words = targetPost.title.split(/[\s,.:;!?]+/).filter((w: string) => w.length > 5);
        if (words.length > 0) {
           // Seleciona a maior palavra do título para ser a Keyword SEO
           const seoKeyword = words.reduce((a: string, b: string) => a.length > b.length ? a : b); 
           
           // Lookbehind/lookahead para evitar links dentro de tags HTML
           const regex = new RegExp(`(?<![<\\/\\[\\-])\\b(${seoKeyword})\\b(?![>\\/\\]\\-])`, 'i'); // Sem 'g' para linkar apenas 1 vez por keyword
           
           cleanMdForParsing = cleanMdForParsing.replace(regex, `<a href="/blog/${targetPost.slug}" class="text-theme-accent hover:underline decoration-theme-accent/50 underline-offset-4 font-semibold" title="Leia também sobre $1">$1</a>`);
        }
      });
    }
  } catch (e) {
    console.error("Erro no SEO Programático (Fase 108):", e);
  }

  // HTML parser setup
  const rawHtml = await unified()
    .use(remarkParse)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSlug)
    .use(rehypeStringify)
    .process(cleanMdForParsing);
    
  // FASE 60: SANITIZAÇÃO ESTRITA DE HTML E PREVENÇÃO DE XSS (DOMPURIFY)
  const contentHtml = DOMPurify.sanitize(String(rawHtml), {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li', 'blockquote', 'img', 'br', 'hr', 'span', 'div', 'code', 'pre', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'svg', 'path'],
    ALLOWED_ATTR: ['href', 'title', 'target', 'rel', 'src', 'alt', 'class', 'className', 'id', 'width', 'height', 'fill', 'stroke', 'viewBox', 'stroke-linecap', 'stroke-linejoin', 'stroke-width', 'd'],
  });

  // FASE 114: Buscar blocos de AdBlock do painel de monetização (Global)
  const inArticleAdRaw = db.prepare(`SELECT scriptCode FROM AdBlock WHERE position = 'article_middle' AND isActive = 1 LIMIT 1`).get() as any;
  const inTextAdHtml = inArticleAdRaw?.scriptCode || null;
  
  const stickyMobileRaw = db.prepare(`SELECT scriptCode FROM AdBlock WHERE position = 'popup' AND isActive = 1 LIMIT 1`).get() as any;
  const stickyMobileHtml = stickyMobileRaw?.scriptCode || null;

  // JSON-LD Schema for Google SEO (NewsArticle + BreadcrumbList)
  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'NewsArticle',
        headline: post.title,
        image: post.coverImage ? [post.coverImage] : [],
        datePublished: new Date(post.publishedAt || post.createdAt).toISOString(),
        dateModified: new Date(post.updatedAt || post.createdAt).toISOString(),
        author: [{
          '@type': 'Person',
          name: post.author,
        }],
        publisher: {
          '@type': 'Organization',
          name: blogMeta?.name || 'Portal',
          logo: {
            '@type': 'ImageObject',
            url: `https://${decodedDomain}/logo.png`
          }
        }
      },
      {
        '@type': 'BreadcrumbList',
        'itemListElement': [
          {
            '@type': 'ListItem',
            'position': 1,
            'name': 'Início',
            'item': `https://${decodedDomain}`
          },
          {
            '@type': 'ListItem',
            'position': 2,
            'name': postCategory ? postCategory.name : 'Geral',
            'item': postCategory ? `https://${decodedDomain}/category/${postCategory.slug}` : `https://${decodedDomain}`
          },
          {
            '@type': 'ListItem',
            'position': 3,
            'name': post.title,
            'item': `https://${decodedDomain}/blog/${slug}`
          }
        ]
      }
    ]
  };

  const wordsCount = post.contentMd.split(/\s+/).length;
  const readingTime = Math.max(1, Math.ceil(wordsCount / 200));

  return (
    <main className={`flex min-h-screen flex-col items-center bg-theme-bg theme-transition text-theme-text ${themeClass}`}>
      <ReadingProgress title={post.title} readingTime={readingTime} />
      <HistoryTracker domain={decodedDomain} slug={slug} title={post.title} />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <ViewTracker postId={post.id} />
      
      <FloatingShare title={post.title} url={`https://${decodedDomain}/blog/${slug}`} />
      
      {/* HEADER NAVBAR (PREMIUM) */}
      <NavbarMaster blog={blogMeta} categories={categories} lang={lang} domain={decodedDomain} />

      <NewsTicker posts={recentPosts} domain={decodedDomain} />

      <div className="zen-content w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 z-10 flex flex-col lg:flex-row gap-10">
        
        {/* COLUNA ESQUERDA - ARTIGO (75%) */}
        <div className="w-full lg:w-3/4">
          
          {/* BREADCRUMB SEMÂNTICO (UI/UX) */}
          <nav aria-label="Breadcrumb" className="flex items-center gap-2 mb-8 text-[11px] md:text-xs font-bold uppercase tracking-widest text-theme-muted overflow-x-auto whitespace-nowrap pb-2 scrollbar-hide">
            <Link href="/" className="hover:text-theme-accent transition-colors flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
              Início
            </Link>
            
            <span className="text-slate-600">/</span>
            
            {postCategory ? (
              <Link href={`/category/${postCategory.slug}`} className="hover:text-theme-accent transition-colors">
                {postCategory.name}
              </Link>
            ) : (
              <span className="text-slate-500">Geral</span>
            )}
            
            <span className="text-slate-600">/</span>
            
            <span className="text-slate-400 max-w-[150px] md:max-w-[300px] truncate">
              {post.title}
            </span>
          </nav>

          {/* HEADER DO ARTIGO */}
          <header className="mb-12 border-b border-theme-border pb-8">

            <h1 className="text-3xl md:text-5xl font-extrabold leading-tight mb-8 text-theme-text">
              {post.title}
            </h1>

            {post.coverImage && (
              <ParallaxCover src={post.coverImage} alt={post.title} />
            )}
            <div className="mt-4 flex flex-col md:flex-row md:items-center justify-between border-t border-theme-border pt-4 gap-4">
               <div className="flex items-center gap-3">
                 <div className="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700 shadow-lg">
                   <svg className="w-5 h-5 text-theme-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                 </div>
                 <div>
                   <p className="text-sm font-bold text-theme-text uppercase tracking-wider">{post.author}</p>
                   <p className="text-[10px] uppercase tracking-widest text-theme-accent font-bold">Redação Especial</p>
                 </div>
               </div>
               
               <div className="flex items-center gap-4 text-xs font-bold text-slate-400 bg-theme-surface/50 p-2 rounded-xl border border-theme-border/50">
                 <span className="flex items-center gap-1.5" title="Data de Publicação">
                   <svg className="w-4 h-4 text-theme-muted" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                   {new Date(post.publishedAt || post.createdAt).toLocaleDateString('pt-BR')}
                 </span>
                 <span className="w-1 h-1 rounded-full bg-slate-600"></span>
                 <span className="flex items-center gap-1.5 text-theme-accent" title="Tempo de Leitura">
                   <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                   {readingTime} MIN LENDO
                 </span>
                 <span className="w-1 h-1 rounded-full bg-slate-600"></span>
                 <span className="flex items-center gap-1.5 text-emerald-400" title="Visualizações">
                   <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                   {/* views fakes baseadas no ID (consistente) + views reais */}
                   {((post.id.split('').reduce((acc: number, char: string) => acc + char.charCodeAt(0), 0) * 142) + (post.views || 0)).toLocaleString('pt-BR')} VISUALIZAÇÕES
                 </span>
               </div>
            </div>
          </header>

          {/* PLAYER DE NARRATIVA IA (Acessibilidade e Retenção de Áudio) */}
          <TextToSpeechPlayer audioUrl={post.audioUrl} />

          {/* VÍDEO PRINCIPAL (Gerado pelo Apollo) */}
          {post.videoUrl && (
            <div className="w-full my-8 rounded-2xl overflow-hidden shadow-2xl border border-theme-border">
              <video 
                controls 
                className="w-full max-h-[600px] bg-black object-contain"
                src={post.videoUrl}
                poster={post.coverImage}
              >
                Seu navegador não suporta a tag de vídeo.
              </video>
            </div>
          )}

          {/* MÓDULO INTERATIVO DE MÍDIA (Áudio, Vídeo Série, Galeria ou Timeline) */}
          <InteractiveMediaRouter
            postType={post.postType}
            mediaPayload={post.mediaPayload}
            primaryColor={blogMeta?.primaryColor || '#06b6d4'}
            secondaryColor={blogMeta?.secondaryColor || '#3b82f6'}
            accentStyle={blogMeta?.accentStyle || 'rounded'}
          />

          {/* RESUMO DA IA (TL;DR) */}
          {tldrContent && <ArticleTLDR content={tldrContent} />}

          {/* CONTEÚDO DO ARTIGO COM PAYWALL NEURAL, LIGHTBOX E TRIGGER WARNING */}
          <SensitiveContentBlocker isSensitive={isSensitive}>
            <ImageLightbox>
              <article className="zen-article bg-theme-surface p-6 md:p-12 rounded-2xl text-lg text-slate-300 leading-relaxed shadow-lg border border-theme-border/50 mb-12">
                <PaywallBlocker contentHtml={contentHtml} inTextAdHtml={inTextAdHtml} blogId={blogMeta?.id} />
              </article>
            </ImageLightbox>
          </SensitiveContentBlocker>
          {/* WIDGET DE NEWSLETTER (FASE 9) */}
          <NewsletterWidget blogId={blogMeta?.id} domain={decodedDomain} />

          {/* GAMIFICAÇÃO & ENGAGEMENT */}
          <ArticleReactions postId={post.id} />

          {/* CAIXA DE AFILIADO / OFERTA NATIVA (CPA - Apenas se houver link real no banco) */}
          {affiliateOffer && (
            <div className="mb-12 bg-gradient-to-br from-theme-accent/20 to-transparent p-[1px] rounded-3xl overflow-hidden relative group animate-float shadow-2xl">
              <div className="absolute inset-0 bg-theme-accent opacity-0 group-hover:opacity-10 transition-opacity duration-1000"></div>
              <div className="bg-theme-bg/90 backdrop-blur-xl p-8 md:p-10 rounded-[23px] flex flex-col md:flex-row items-center justify-between gap-8 relative z-10">
                <div className="flex-1 text-center md:text-left">
                  <div className="inline-block px-3 py-1 bg-red-500/10 text-red-500 font-black text-[10px] uppercase tracking-widest rounded-full mb-3 border border-red-500/20">
                    Recomendação Especial
                  </div>
                  <h3 className="text-2xl md:text-3xl font-black text-white mb-2">{affiliateOffer.keyword || "Desbloqueie o Próximo Nível"}</h3>
                  <p className="text-slate-400 font-medium leading-relaxed max-w-lg">
                    Descubra as estratégias e ferramentas recomendadas pela nossa redação para impulsionar seus resultados.
                  </p>
                </div>
                <div className="w-full md:w-auto shrink-0">
                  <a href={affiliateOffer.url} target="_blank" rel="noopener nofollow" className="w-full md:w-auto block bg-theme-accent hover:bg-theme-accent-hover text-white font-black px-10 py-5 rounded-2xl text-center shadow-[0_0_20px_rgba(var(--theme-accent-rgb),0.3)] hover:shadow-[0_0_30px_rgba(var(--theme-accent-rgb),0.5)] transition-all hover:-translate-y-1">
                    ACESSAR AGORA →
                  </a>
                </div>
              </div>
            </div>
          )}

          {/* SESSÃO DE DOAÇÃO / GORJETA (FASE 82) */}
          <DonationTipJar 
             pixKey={process.env.DONATION_PIX_KEY} 
             cryptoWallet={process.env.DONATION_WALLET_ETH} 
          />

          {/* SESSÃO DE COMENTÁRIOS DA COMUNIDADE (GHOST COMMUNITY + INTERATIVIDADE FAKE) */}
          <ArticleComments initialComments={comments} />

          {/* AUTHOR BOX */}
          <div className="bg-theme-surface border border-theme-border rounded-xl p-8 flex flex-col sm:flex-row gap-6 items-center sm:items-start shadow-lg mb-12 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-32 h-32 bg-theme-accent/5 rounded-full blur-2xl pointer-events-none -mr-16 -mt-16 group-hover:bg-theme-accent/10 transition-colors"></div>
            <div className="w-24 h-24 rounded-full bg-cyan-900/50 flex-shrink-0 flex items-center justify-center border-2 border-cyan-700 relative z-10 shadow-inner">
               <svg className="w-10 h-10 text-theme-accent-hover" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            </div>
            <div className="relative z-10 text-center sm:text-left">
              <h3 className="text-xl font-bold text-theme-text mb-2">{post.author}</h3>
              <p className="text-sm text-theme-muted leading-relaxed mb-4">
                Este artigo foi apurado e redigido pela equipe de especialistas do {blogMeta?.name || 'Portal'}. Nossa redação monitora constantemente os dados do mercado para fornecer análises com velocidade e precisão jornalística.
              </p>
              <Link href={`/author/${(post.author || 'redacao').toLowerCase().replace(/\s+/g, '-')}`} className="inline-block text-xs font-bold text-theme-accent hover:text-white bg-theme-accent/10 hover:bg-theme-accent px-4 py-2 rounded-lg transition-all duration-300 uppercase tracking-widest border border-theme-accent/20">
                Ver Perfil e Artigos
              </Link>
            </div>
          </div>

          {/* ChatGPT SEO BAIT */}
          <ChatGPTBait domain={decodedDomain} slug={slug} title={post.title} />

          <RelatedPosts currentPostId={post.id} domain={decodedDomain} />

        </div>

        {/* COLUNA DIREITA - SIDEBAR (25%) */}
        <aside className="w-full lg:w-1/4 hidden lg:block">
          <div className="sticky top-24 space-y-8">
            <TableOfContents contentMd={post.contentMd} />
            <NewsletterWidget blogId={blogMeta?.id} domain={decodedDomain} />
            
            {/* INJEÇÃO DE PUBLICIDADE NA SIDEBAR (MONETIZAÇÃO) */}
            <AdBanner type="sidebar" domain={decodedDomain} />

            {/* Widget Top Posts */}
            <div className="bg-theme-surface/80 backdrop-blur-md p-6 rounded-2xl border border-theme-border/60 shadow-xl">
              <h3 className="text-theme-text font-black mb-6 uppercase tracking-widest text-sm flex items-center gap-2">
                <span className="w-2 h-4 bg-theme-accent rounded-sm inline-block"></span>
                Em Alta
              </h3>
              <div className="space-y-5">
                {otherPosts.slice(0, 4).map((post: any, i: number) => (
                  <Link key={post.id} href={`/blog/${post.slug}`} className="flex gap-4 group items-start">
                    <span className="text-4xl font-black text-slate-800/80 group-hover:text-theme-accent transition-colors italic leading-none">{i+1}</span>
                    <h4 className="text-sm font-semibold text-slate-300 group-hover:text-white transition-colors line-clamp-3 leading-relaxed mt-1">
                      {post.title}
                    </h4>
                  </Link>
                ))}
              </div>
            </div>

            <ReadingHistory domain={decodedDomain} />

            <AdBanner type="vertical" domain={decodedDomain} />
          </div>
        </aside>

      </div>
      
      <ArticleChatbot articleContext={post.contentMd} />
      <ExitIntentPopup blogId={blogMeta?.id || ''} />
      <MobileStickyAd adHtml={stickyMobileHtml} />
      <ScrollToTop />
      {otherPosts.length > 0 && <FloatingReadMore post={otherPosts[0]} domain={decodedDomain} />}
      <InteractiveBlockquotes />
      <Footer domain={decodedDomain} name={blogMeta?.name} />
    </main>
  );
}
