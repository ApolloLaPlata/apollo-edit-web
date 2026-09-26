import { MetadataRoute } from 'next';
import db from '@/lib/db';

export default async function manifest(props: { params: Promise<{ domain: string }> }): Promise<MetadataRoute.Manifest> {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);

  let blogName = 'Auto-Blog CMS';
  let primaryColor = '#dc2626';

  try {
     const blog = await db.prepare('SELECT name, primaryColor FROM Blog WHERE domain = ?').get(decodedDomain) as any;
     if (blog) {
       blogName = blog.name;
       primaryColor = blog.primaryColor || '#dc2626';
     }
  } catch(e) {}

  return {
    name: blogName,
    short_name: blogName.substring(0, 12),
    description: `Notícias e Fofocas do ${blogName}`,
    start_url: '/',
    display: 'standalone',
    background_color: '#0f172a',
    theme_color: primaryColor,
    icons: [
      {
        src: '/favicon.ico',
        sizes: 'any',
        type: 'image/x-icon',
      },
      {
        src: '/icon-192.png',
        sizes: '192x192',
        type: 'image/png',
      },
      {
        src: '/icon-512.png',
        sizes: '512x512',
        type: 'image/png',
      },
    ],
  };
}
