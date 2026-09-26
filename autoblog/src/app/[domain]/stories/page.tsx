import { Metadata } from 'next';
import db from '@/lib/db';
import WebStoryPlayer from '@/components/blog/WebStoryPlayer';

export async function generateMetadata(props: { params: Promise<{ domain: string }> }): Promise<Metadata> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  
  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }

  return {
    title: `Web Stories | ${blogMeta?.name || 'Portal'}`,
    description: `Assista aos conteúdos mais rápidos e visuais do ${blogMeta?.name || 'nosso portal'}.`,
    alternates: {
      canonical: `https://${decodedDomain}/stories`
    }
  };
}

export default async function StoriesPage(props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);
  
  let blogMeta = await db.prepare('SELECT * FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  if (!blogMeta && decodedDomain.includes('localhost')) {
    blogMeta = await db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }
  const themeClass = blogMeta?.theme ? `theme-${blogMeta.theme}` : 'theme-dark';

  // Buscar os stories no Banco de Dados
  let stories = [];
  try {
    stories = await db.prepare(`
      SELECT * FROM WebStory 
      WHERE blogId = ? 
      ORDER BY createdAt DESC LIMIT 20
    `).all(blogMeta?.id) as any[];
  } catch (e) {
    console.error("A tabela WebStory ainda não existe ou ocorreu um erro.", e);
  }

  return (
    <main className={`flex min-h-screen flex-col bg-black text-white ${themeClass}`}>
      {/* O componente WebStoryPlayer renderizará toda a tela (Client Component) */}
      <WebStoryPlayer initialStories={stories} domain={decodedDomain} />
    </main>
  );
}
