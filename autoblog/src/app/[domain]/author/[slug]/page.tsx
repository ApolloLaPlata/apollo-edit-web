import { Metadata } from 'next';
import Link from 'next/link';
import db from '@/lib/db';
import SearchBar from '@/components/blog/SearchBar';
import Footer from '@/components/blog/Footer';

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
  if (!blogMeta) return { title: 'Autor não encontrado' };

  const authorName = slug.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');

  return {
    title: `${authorName} | Equipe ${blogMeta.name}`,
    description: `Perfil e histórico de artigos escritos por ${authorName} para o ${blogMeta.name}.`,
    alternates: {
      canonical: `https://${decodedDomain}/author/${slug}`
    }
  };
}

export default async function AuthorPage(props: { params: Promise<{ domain: string, slug: string }>, searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const decodedDomain = decodeURIComponent(params.domain);
  const slug = decodeURIComponent(params.slug);
  const lang = (typeof searchParams.lang === 'string') ? searchParams.lang : 'pt';
  
  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';

  let authorName = slug.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
  if (slug.includes('redacao')) {
    authorName = 'Redação Especial';
  }

  let posts = [] as any[];
  if (slug.includes('redacao')) {
     posts = await db.prepare(`
        SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
        FROM Post 
        LEFT JOIN Blog ON Post.blogId = Blog.id 
        WHERE Post.blogId = ? AND Post.language = ? AND Post.isPublished = 1
        AND (Post.author LIKE '%Redação%' OR Post.author IS NULL OR Post.author = '')
        ORDER BY Post.createdAt DESC LIMIT 20
      `).all(blogMeta?.id, lang) as any[];
  } else {
     posts = await db.prepare(`
        SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
        FROM Post 
        LEFT JOIN Blog ON Post.blogId = Blog.id 
        WHERE Post.blogId = ? AND Post.language = ? AND Post.isPublished = 1
        AND Post.author LIKE ?
        ORDER BY Post.createdAt DESC LIMIT 20
      `).all(blogMeta?.id, lang, `%${authorName}%`) as any[];
  }

  const categories = await db.prepare(`SELECT name, slug FROM Category WHERE blogId = ? LIMIT 4`).all(blogMeta?.id) as any[];

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
        'name': 'Equipe Editorial',
        'item': `https://${decodedDomain}`
      },
      {
        '@type': 'ListItem',
        'position': 3,
        'name': authorName,
        'item': `https://${decodedDomain}/author/${slug}`
      }
    ]
  };

  return (
    <main className={`flex min-h-screen flex-col items-center bg-theme-bg theme-transition text-theme-text ${themeClass}`}>
      
      {/* HEADER NAVBAR PREMIUM */}
      <nav className="sticky top-0 w-full z-50 transition-all duration-300 bg-theme-bg/50 backdrop-blur-md border-b border-theme-border/50 py-4 shadow-xl">
        <div className="max-w-7xl mx-auto px-4 py-2 flex justify-between items-center">
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
              <Link key={cat.slug} href={`/category/${cat.slug}`} className="hover:text-theme-accent-hover transition-colors uppercase tracking-wider text-[11px]">{cat.name}</Link>
            )) : (
              <Link href="/" className="hover:text-theme-accent-hover transition-colors uppercase tracking-wider text-[11px]">Destaques</Link>
            )}
            <SearchBar domain={decodedDomain} lang={lang} />
          </div>
        </div>
      </nav>

      {/* AUTHOR BIO CARD */}
      <div className="w-full relative overflow-hidden bg-gradient-to-br from-theme-surface to-slate-900 border-b border-theme-border/50 py-16">
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
        <div className="absolute top-0 right-0 w-96 h-96 bg-theme-accent/5 rounded-full blur-3xl pointer-events-none -mr-32 -mt-32" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          {/* BREADCRUMB SEMÂNTICO (UI/UX) */}
          <nav aria-label="Breadcrumb" className="flex items-center gap-2 mb-10 text-[11px] font-bold uppercase tracking-widest text-theme-muted">
            <Link href="/" className="hover:text-theme-accent transition-colors flex items-center gap-1">
              Início
            </Link>
            <span className="text-slate-600">/</span>
            <span>Equipe Editorial</span>
            <span className="text-slate-600">/</span>
            <span className="text-theme-accent truncate max-w-[150px]">
              {authorName}
            </span>
          </nav>
          
          <div className="flex flex-col md:flex-row items-center gap-10">
            <div className="w-32 h-32 md:w-48 md:h-48 rounded-full border-4 border-theme-accent/20 bg-theme-bg/80 flex items-center justify-center flex-shrink-0 shadow-2xl relative overflow-hidden">
             {/* Avatar Genérico Profissional */}
             <div className="absolute inset-0 bg-gradient-to-tr from-theme-accent/20 to-transparent"></div>
             <span className="text-5xl md:text-7xl">🖋️</span>
          </div>
          <div className="text-center md:text-left">
            <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-theme-accent/10 border border-theme-accent/20 text-theme-accent text-[10px] font-black uppercase tracking-widest mb-4">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              Equipe Verificada E-E-A-T
            </span>
            <h1 className="text-4xl md:text-6xl font-black text-white tracking-tight mb-2">{authorName}</h1>
            <p className="text-slate-400 text-lg md:text-xl font-medium max-w-2xl">
              {slug.includes('redacao') 
                ? `Coletivo de jornalistas e especialistas do ${blogMeta?.name}, focado em produzir análises profundas, checagem de fatos e reportagens imparciais.`
                : `Jornalista especializado e colaborador fixo do ${blogMeta?.name}, trazendo visões precisas e reportagens diretas da fonte.`
              }
            </p>
          </div>
        </div>
        </div>
      </div>

      {/* POSTS GRID */}
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-2xl font-bold mb-8 flex items-center gap-3">
          <span className="w-1.5 h-8 bg-theme-accent rounded-full"></span>
          Artigos Publicados
        </h2>

        {posts.length === 0 ? (
           <div className="py-20 text-center text-theme-muted flex flex-col items-center justify-center bg-theme-surface/50 rounded-3xl border border-theme-border/50">
             <span className="text-5xl mb-4 opacity-50">📂</span>
             <p className="font-bold text-lg tracking-wide text-slate-300">Nenhuma publicação registrada.</p>
           </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {posts.map((post: any) => (
              <div key={post.id} className="bg-theme-surface/70 backdrop-blur-md rounded-2xl overflow-hidden border border-theme-border/60 shadow-lg group hover:border-theme-accent/50 hover:shadow-theme-accent/10 hover:-translate-y-1 transition-all duration-300 flex flex-col">
                <Link href={`/blog/${post.slug}`} className="block">
                  <div className="h-48 w-full relative overflow-hidden bg-slate-900 border-b border-theme-border/50">
                    {post.coverImage ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={post.coverImage} alt={post.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out" />
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-theme-surface">
                         <span className="text-3xl opacity-20 mb-2">📸</span>
                      </div>
                    )}
                  </div>
                </Link>
                <div className="p-6 flex flex-col flex-grow">
                  <Link href={`/blog/${post.slug}`}>
                    <h3 className="text-lg font-black text-theme-text mb-3 leading-snug group-hover:text-theme-accent transition-colors line-clamp-2" title={post.title}>
                      {post.title}
                    </h3>
                  </Link>
                  <p className="text-sm text-theme-muted mb-6 line-clamp-3 font-medium leading-relaxed">
                    {cleanExcerpt(post.contentMd).substring(0, 100)}...
                  </p>
                  <div className="mt-auto flex justify-between items-center text-[10px] text-theme-muted uppercase tracking-wider font-bold pt-4 border-t border-theme-border/50">
                    <span className="flex items-center gap-2">
                       <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
                       {new Date(post.createdAt).toLocaleDateString('pt-BR')}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Footer domain={decodedDomain} name={blogMeta?.name} />
    </main>
  );
}
