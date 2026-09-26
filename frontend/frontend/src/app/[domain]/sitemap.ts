import { MetadataRoute } from 'next';
import db from '@/lib/db';

// Geração do Sitemap Dinâmico via Next.js nativo (Multi-Tenant)
export default async function sitemap({ params }: { params: Promise<{ domain: string }> }): Promise<MetadataRoute.Sitemap> {
  const resolvedParams = await params;
  const decodedDomain = decodeURIComponent(resolvedParams.domain);
  const baseUrl = `https://${decodedDomain}`;

  // Busca ID do blog
  const blog = db.prepare('SELECT id FROM Blog WHERE domain = ?').get(decodedDomain) as any;
  const blogId = blog ? blog.id : 0;

  // Busca os últimos 5.000 posts (limite recomendável do Google Search Console)
  const posts = db.prepare(`
    SELECT slug, updatedAt 
    FROM Post 
    WHERE blogId = ? AND isPublished = 1 
    ORDER BY createdAt DESC LIMIT 5000
  `).all(blogId) as any[];

  const postUrls = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt || Date.now()),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }));

  // Busca as Categorias
  const categories = db.prepare('SELECT slug FROM Category WHERE blogId = ?').all(blogId) as any[];
  const categoryUrls = categories.map((cat) => ({
    url: `${baseUrl}/category/${cat.slug}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: 0.6,
  }));

  // Busca Autores (SEO E-E-A-T)
  const authorsRaw = db.prepare(`SELECT DISTINCT author FROM Post WHERE blogId = ? AND author IS NOT NULL AND author != ''`).all(blogId) as any[];
  const authorUrls = authorsRaw.map((row) => ({
    url: `${baseUrl}/author/${row.author.toLowerCase().replace(/\s+/g, '-')}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }));

  // Rotas institucionais Core
  const coreRoutes = [
    '',
    '/about',
    '/contact',
    '/privacy',
    '/ofertas',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: route === '' ? 'hourly' as const : 'monthly' as const,
    priority: route === '' ? 1.0 : 0.3,
  }));

  return [...coreRoutes, ...categoryUrls, ...authorUrls, ...postUrls];
}
