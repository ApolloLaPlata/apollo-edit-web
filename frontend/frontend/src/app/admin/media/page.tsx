import React from 'react';
import db from '@/lib/db';
import MediaClient from './MediaClient';

export const dynamic = 'force-dynamic';

export default async function MediaLibraryPage() {
  // Buscar todas as imagens de capa dos posts com os nomes dos portais
  const mediaItems = db
    .prepare(`
    SELECT Post.id, Post.title, Post.slug, Post.coverImage, Post.createdAt, Post.blogId, Blog.name as blogName, Blog.domain as blogDomain 
    FROM Post 
    LEFT JOIN Blog ON Post.blogId = Blog.id
    WHERE Post.coverImage IS NOT NULL AND Post.coverImage != ''
    ORDER BY Post.createdAt DESC
  `)
    .all() as any[];

  const blogs = db.prepare('SELECT id, name, domain FROM Blog ORDER BY name ASC').all() as any[];

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      <MediaClient initialMedia={mediaItems} blogs={blogs} />
    </div>
  );
}
