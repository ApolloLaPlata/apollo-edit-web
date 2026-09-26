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

export async function generateMetadata(props: { params: Promise<{ domain: string }>, searchParams: Promise<{ [key: string]: string | string[] | undefined }> }): Promise<Metadata> {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const decodedDomain = decodeURIComponent(params.domain);
  const q = (typeof searchParams.q === 'string') ? searchParams.q : '';

  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }

  return {
    title: `Resultados para "${q}" | ${blogMeta?.name || 'Busca'}`,
    description: `Buscando resultados e artigos sobre ${q} no ${blogMeta?.name || 'nosso portal'}.`,
    robots: { index: false, follow: false } // Evita indexar infinitas urls de busca no Google
  };
}

export default async function SearchPage(props: { params: Promise<{ domain: string }>, searchParams: Promise<{ [key: string]: string | string[] | undefined }> }) {
  const params = await props.params;
  const searchParams = await props.searchParams;
  const decodedDomain = decodeURIComponent(params.domain);
  const lang = (typeof searchParams.lang === 'string') ? searchParams.lang : 'pt';
  const q = (typeof searchParams.q === 'string') ? searchParams.q : '';
  
  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';

  let posts = [] as any[];
  
  if (q.trim().length >= 2) {
      const searchTerm = `%${q}%`;
      posts = await db.prepare(`
        SELECT Post.*, Blog.name as blog_name, Blog.domain as blog_domain
        FROM Post 
        LEFT JOIN Blog ON Post.blogId = Blog.id 
        WHERE Post.blogId = ? AND Post.language = ? AND Post.isPublished = 1
        AND (Post.title LIKE ? OR Post.contentMd LIKE ?)
        ORDER BY Post.createdAt DESC LIMIT 30
      `).all(blogMeta?.id, lang, searchTerm, searchTerm) as any[];
  }

  const categories = await db.prepare(`SELECT name, slug FROM Category WHERE blogId = ? LIMIT 4`).all(blogMeta?.id) as any[];

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

      {/* SEARCH HEADER */}
      <div className="w-full bg-slate-900 border-b border-theme-border/50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span className="text-theme-accent font-bold text-[10px] uppercase tracking-widest mb-4 block">Motor de Pesquisa do Portal</span>
          
          {q ? (
             <>
               <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">
                 Resultados para <span className="text-theme-accent">"{q}"</span>
               </h1>
               <p className="text-slate-400 mt-2 max-w-xl mx-auto">
                 Encontramos {posts.length} {posts.length === 1 ? 'matéria' : 'matérias'} nos nossos arquivos.
               </p>
             </>
          ) : (
             <>
               <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight mb-2">Pesquisa Central</h1>
               <p className="text-slate-400 mt-2 max-w-xl mx-auto">Digite um termo na barra de busca superior para localizar matérias.</p>
             </>
          )}
        </div>
      </div>

      {/* POSTS GRID */}
      <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {q && posts.length === 0 ? (
           <div className="py-24 text-center text-theme-muted flex flex-col items-center justify-center bg-theme-surface/30 rounded-3xl border border-theme-border/50">
             <span className="text-5xl mb-4 opacity-50">🔍</span>
             <p className="font-bold text-xl tracking-wide text-white">Nenhum resultado encontrado.</p>
             <p className="text-sm mt-2 opacity-70">Tente buscar por termos mais genéricos, categorias ou palavras diferentes.</p>
             <Link href="/" className="mt-8 px-6 py-3 bg-theme-accent/20 text-theme-accent font-bold uppercase tracking-widest text-[11px] rounded-lg border border-theme-accent/30 hover:bg-theme-accent hover:text-white transition-all">
                Voltar à Página Inicial
             </Link>
           </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
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
                    <span className="text-theme-accent px-2 py-1 bg-theme-accent/10 rounded-md">{(post.author || '').replace(/Redação IA/gi, post.blog_name || 'Equipe Especial') || post.blog_name || 'Redação'}</span>
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
