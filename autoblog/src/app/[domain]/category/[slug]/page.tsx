import { Metadata } from 'next';
import Link from 'next/link';
import db from '@/lib/db';
import AdBanner from '@/components/blog/AdBanner';
import SearchBar from '@/components/blog/SearchBar';
import Footer from '@/components/blog/Footer';

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

export async function generateMetadata(props: { params: Promise<{ domain: string, slug: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);

  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  if (!blogMeta) return { title: 'Blog não encontrado' };

  const category = await db.prepare('SELECT name FROM Category WHERE slug = ? AND blogId = ?').get(slug, blogMeta.id) as any;
  if (!category) return { title: 'Categoria não encontrada' };

  return {
    title: `${category.name} | ${blogMeta.name}`,
    description: `Artigos e análises sobre ${category.name} publicados pelo ${blogMeta.name}.`,
    alternates: {
      canonical: `https://${decodedDomain}/category/${slug}`
    }
  };
}

import { unstable_cache } from 'next/cache';

const getCachedBlog = unstable_cache(
  async (domain: string) => {
    let blog = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(domain) as any;
    if (!blog && domain.includes('localhost')) {
      blog = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
    }
    return blog;
  },
  ['blog-config-category'],
  { revalidate: 3600 }
);

const getCachedCategoryInfo = unstable_cache(
  async (slug: string, blogId: string) => {
    return await db.prepare('SELECT id, name, slug FROM Category WHERE slug = ? AND blogId = ?').get(slug, blogId) as any;
  },
  ['blog-category-info'],
  { revalidate: 3600 }
);

const getCachedCategoryPosts = unstable_cache(
  async (blogId: string, categoryId: string, lang: string) => {
    return await db.prepare(`
      SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
      FROM Post 
      LEFT JOIN Blog ON Post.blogId = Blog.id 
      WHERE Post.blogId = ? AND Post.categoryId = ? AND Post.language = ? AND Post.isPublished = 1
      ORDER BY Post.createdAt DESC LIMIT 20
    `).all(blogId, categoryId, lang) as any[];
  },
  ['blog-category-posts'],
  { revalidate: 60 }
);

const getCachedCategoriesList = unstable_cache(
  async (blogId: string) => {
    return await db.prepare(`SELECT name, slug FROM Category WHERE blogId = ? LIMIT 4`).all(blogId) as any[];
  },
  ['blog-sidebar-categories'],
  { revalidate: 3600 }
);

export default async function CategoryPage(props: { params: Promise<{ domain: string, slug: string }>, searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);
  const lang = (typeof searchParams.lang === 'string') ? searchParams.lang : 'pt';
  
  const blogMeta = await getCachedBlog(decodedDomain);
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';

  const category = await getCachedCategoryInfo(slug, blogMeta?.id);

  let posts = [] as any[];
  if (category) {
    posts = await getCachedCategoryPosts(blogMeta?.id, category.id, lang);
  }

  const categories = await getCachedCategoriesList(blogMeta?.id);

  // JSON-LD Schema for Google SEO (BreadcrumbList)
  const jsonLd = {
    '@context': 'https://schema.org',
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
        'name': category ? category.name : 'Categoria',
        'item': `https://${decodedDomain}/category/${slug}`
      }
    ]
  };

  return (
    <main className={`flex min-h-screen flex-col items-center bg-theme-bg theme-transition text-theme-text ${themeClass}`}>

      {/* HEADER NAVBAR (Estética Glassmorphism Premium) */}
      <nav className="sticky top-0 w-full z-50 transition-all duration-300 bg-theme-bg/50 backdrop-blur-md border-b border-theme-border/50 py-4 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <Link href={`/?lang=${lang}`} className="flex items-center gap-2">
            <div className="w-8 h-8 bg-theme-accent rounded flex items-center justify-center">
              <span className="text-theme-text font-bold font-serif text-sm">{blogMeta?.name?.charAt(0) || "O"}</span>
            </div>
            <span className="font-bold text-xl tracking-tight text-theme-text uppercase hidden sm:block">
              {blogMeta?.name}
            </span>
          </Link>
          <div className="flex gap-4 sm:gap-6 text-sm font-semibold text-slate-300 items-center">
            {categories.length > 0 ? categories.map((cat) => (
              <Link key={cat.slug} href={`/category/${cat.slug}`} className={`hover:text-theme-accent-hover transition-colors uppercase tracking-wider text-[11px] ${cat.slug === slug ? 'text-theme-accent font-bold' : ''}`}>{cat.name}</Link>
            )) : (
              <Link href="/" className="hover:text-theme-accent-hover transition-colors uppercase tracking-wider text-[11px]">Destaques</Link>
            )}
            <SearchBar domain={decodedDomain} lang={lang} />
          </div>
        </div>
      </nav>

      {/* CATEGORY HEADER PREMIUM */}
      <div className="w-full relative overflow-hidden bg-gradient-to-b from-theme-surface to-theme-bg border-b border-theme-border/50 py-16">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <div className="absolute top-0 right-0 w-96 h-96 bg-theme-accent/5 rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10 flex flex-col items-center">
          {/* BREADCRUMB SEMÂNTICO (UI/UX) */}
          <nav aria-label="Breadcrumb" className="flex items-center gap-2 mb-6 text-[11px] font-bold uppercase tracking-widest text-theme-muted">
            <Link href="/" className="hover:text-theme-accent transition-colors flex items-center gap-1">
              Início
            </Link>
            <span className="text-slate-600">/</span>
            <span className="text-theme-accent">
              {category?.name || 'Geral'}
            </span>
          </nav>
          
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-theme-accent/10 border border-theme-accent/20 text-theme-accent text-[10px] font-black uppercase tracking-widest mb-4">
              <span className="w-2 h-2 rounded-full bg-theme-accent animate-ping" />
              Explorando a Categoria
          </span>
          <h1 className="text-4xl md:text-5xl font-black text-theme-text tracking-tight">{category?.name || 'Categoria Desconhecida'}</h1>
          <p className="text-slate-400 mt-4 max-w-xl mx-auto text-sm md:text-base font-medium">Leia os artigos mais recentes sobre {category?.name || 'este tema'} produzidos pela nossa equipe especializada.</p>
        </div>
      </div>

      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex flex-col lg:flex-row gap-12">
        
        {/* POSTS GRID (75%) */}
        <div className="w-full lg:w-3/4">
          {posts.length === 0 ? (
             <div className="py-20 text-center text-theme-muted flex flex-col items-center justify-center bg-theme-surface/50 rounded-3xl border border-theme-border/50">
               <span className="text-5xl mb-4 opacity-50">📂</span>
               <p className="font-bold text-lg tracking-wide text-slate-300">Nenhuma publicação nesta categoria.</p>
               <p className="text-sm mt-2 opacity-70">A redação ainda não produziu conteúdos sobre este tema.</p>
             </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {posts.map((post: any) => (
                <div key={post.id} className="bg-theme-surface/70 backdrop-blur-md rounded-2xl overflow-hidden border border-theme-border/60 shadow-lg group hover:border-theme-accent/50 hover:shadow-theme-accent/10 hover:-translate-y-1 transition-all duration-300 flex flex-col">
                  <Link href={`/blog/${post.slug}`} className="block">
                    <div className="h-52 w-full relative overflow-hidden bg-slate-900 border-b border-theme-border/50">
                      {post.coverImage ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" />
                      ) : (
                        <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-theme-surface">
                           <span className="text-3xl opacity-20 mb-2">📸</span>
                           <span className="text-[10px] uppercase tracking-widest font-bold text-slate-600">Mídia Indisponível</span>
                        </div>
                      )}
                    </div>
                  </Link>
                  <div className="p-6 flex flex-col flex-grow">
                    <span className="text-theme-accent font-bold text-[10px] uppercase tracking-widest mb-3">{category?.name}</span>
                    <Link href={`/blog/${post.slug}`}>
                      <h3 className="text-xl font-black text-theme-text mb-3 leading-snug group-hover:text-theme-accent transition-colors line-clamp-2" title={post.title}>
                        {post.title}
                      </h3>
                    </Link>
                    <p className="text-sm text-theme-muted mb-6 line-clamp-3 font-medium leading-relaxed">
                      {cleanExcerpt(post.contentMd).substring(0, 140)}...
                    </p>
                    <div className="mt-auto flex justify-between items-center text-[10px] text-theme-muted uppercase tracking-wider font-bold pt-4 border-t border-theme-border/50">
                      <span className="flex items-center gap-2">
                         <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                         {new Date(post.createdAt).toLocaleDateString('pt-BR')}
                      </span>
                      <span className="text-theme-accent px-2 py-1 bg-theme-accent/10 rounded-md">{(post.author || '').replace(/Redação IA/gi, post.blog_name || 'Equipe Especial') || post.blog_name || 'Redação'}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* SIDEBAR (25%) */}
        <aside className="w-full lg:w-1/4 space-y-8">
          <div className="sticky top-24 space-y-8">
            <AdBanner type="square" domain={decodedDomain} />
            <div className="bg-theme-surface/80 backdrop-blur-md p-6 rounded-2xl border border-theme-border/60 shadow-xl">
              <h3 className="text-theme-text font-black mb-4 uppercase tracking-widest text-sm flex items-center gap-2">
                <span className="w-2 h-4 bg-theme-accent rounded-sm inline-block"></span>
                Publicidade
              </h3>
              <AdBanner type="vertical" domain={decodedDomain} />
            </div>
          </div>
        </aside>

      </div>

      <Footer domain={decodedDomain} name={blogMeta?.name} />
    </main>
  );
}
