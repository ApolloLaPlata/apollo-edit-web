import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';
import NavbarMaster from '@/components/ui/NavbarMaster';
import Footer from '@/components/blog/Footer';
import NewsTicker from '@/components/blog/NewsTicker';

export async function generateMetadata(props: { params: Promise<{ domain: string; slug: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const tagName = decodeURIComponent(params.slug).replace(/-/g, ' ');
  const blog = await db.prepare('SELECT name FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  
  return {
    title: `Arquivo da Tag: ${tagName.toUpperCase()} | ${blog?.name || decodedDomain}`,
    description: `Artigos, análises e notícias recentes com a tag ${tagName}.`,
  };
}

export default async function TagPage(props: { params: Promise<{ domain: string; slug: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  const tagSlug = decodeURIComponent(params.slug);
  const tagName = tagSlug.replace(/-/g, ' ');

  const blog = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blog && !decodedDomain.includes('localhost')) notFound();
  
  // Buscar posts que contenham a tag no título ou no conteúdo, simulando relacionamento (ou na tabela de tags se houver, mas assumindo SQLite flat text lookup)
  // Utilizaremos Like para SEO Long-tail
  const posts = await db.prepare(`
    SELECT Post.* 
    FROM Post 
    WHERE blogId = ? AND isPublished = 1 AND (title LIKE ? OR contentMd LIKE ?)
    ORDER BY createdAt DESC LIMIT 30
  `).all(blog?.id || 0, `%${tagName}%`, `%${tagName}%`) as any[];

  const categories = await db.prepare('SELECT * FROM Category WHERE blogId = ?').all(blog?.id || 0) as any[];
  const recentPosts = await db.prepare('SELECT title, slug FROM Post WHERE blogId = ? AND isPublished = 1 ORDER BY createdAt DESC LIMIT 5').all(blog?.id || 0) as any[];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <NavbarMaster blog={blog} categories={categories} lang="pt" domain={decodedDomain} />
      <NewsTicker posts={recentPosts} domain={decodedDomain} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 flex-1 w-full">
        <header className="mb-12 border-b-2 border-red-600 pb-4 inline-block">
          <h1 className="text-4xl md:text-5xl font-black text-slate-900 tracking-tighter uppercase">
            # {tagName}
          </h1>
          <p className="text-slate-500 font-semibold mt-2">
             {posts.length} {posts.length === 1 ? 'resultado encontrado' : 'resultados encontrados'} para esta tag no banco de dados.
          </p>
        </header>

        {posts.length === 0 ? (
           <div className="py-20 text-center border border-dashed border-slate-300 rounded-2xl bg-white">
              <span className="text-5xl mb-4 block">🔍</span>
              <h3 className="text-xl font-bold text-slate-700">Nenhuma matéria arquivada com essa tag.</h3>
              <p className="text-slate-500">Nossa Inteligência Artificial ainda não catalogou artigos sobre este micro-nicho.</p>
           </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {posts.map((post) => (
              <Link key={post.id} href={`/blog/${post.slug}`} className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-2xl border border-slate-200 transition-all hover:-translate-y-2 flex flex-col h-full">
                <div className="h-48 w-full bg-slate-900 overflow-hidden relative">
                   {post.coverImage ? (
                      /* eslint-disable-next-line @next/next/no-img-element */
                      <img src={post.coverImage} alt={post.title} loading="lazy" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out" />
                   ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-slate-700 font-black uppercase tracking-widest text-sm bg-slate-100">Sem Foto</div>
                   )}
                   <div className="absolute top-3 left-3 bg-red-600 text-white text-[10px] uppercase font-black px-2 py-1 rounded shadow-md tracking-wider">
                     LER REPORTAGEM
                   </div>
                </div>
                <div className="p-6 flex-1 flex flex-col">
                  <h2 className="text-lg font-black text-slate-800 leading-snug group-hover:text-red-600 transition-colors line-clamp-3 mb-4">
                    {post.title}
                  </h2>
                  <div className="mt-auto flex items-center justify-between text-xs font-bold text-slate-400 uppercase tracking-widest border-t border-slate-100 pt-4">
                    <span>{new Date(post.createdAt).toLocaleDateString('pt-BR')}</span>
                    <span className="text-red-600">Acessar ↗</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
      <Footer domain={decodedDomain} name={blog?.name} />
    </div>
  );
}
