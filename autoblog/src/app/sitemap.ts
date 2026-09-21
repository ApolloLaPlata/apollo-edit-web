import { MetadataRoute } from 'next';
import { headers } from 'next/headers';
import db from '@/lib/db';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const headersList = await headers();
  const domain = headersList.get('host') || 'localhost:3000';
  
  // Localhost fallback
  let blogMeta = db.prepare('SELECT * FROM Blog WHERE domain = ?').get(domain) as any;
  if (!blogMeta && domain.includes('localhost')) {
    blogMeta = db.prepare('SELECT * FROM Blog LIMIT 1').get() as any;
  }

  const baseUrl = `https://${domain}`;

  // Default Home
  const routes: MetadataRoute.Sitemap = [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'hourly',
      priority: 1,
    }
  ];

  if (blogMeta) {
    // Busca os posts
    const posts = db.prepare(`SELECT slug, updatedAt, createdAt FROM Post WHERE blogId = ?`).all(blogMeta.id) as any[];
    posts.forEach(post => {
      routes.push({
        url: `${baseUrl}/blog/${post.slug}`,
        lastModified: new Date(post.updatedAt || post.createdAt),
        changeFrequency: 'daily',
        priority: 0.8,
      });
    });

    // Busca as categorias
    const categories = db.prepare(`SELECT slug FROM Category WHERE blogId = ?`).all(blogMeta.id) as any[];
    categories.forEach(cat => {
      routes.push({
        url: `${baseUrl}/category/${cat.slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.6,
      });
    });
  }

  return routes;
}
