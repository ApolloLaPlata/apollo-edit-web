import React from 'react';
import db from '@/lib/db';
import PostsClient from './PostsClient';

export default async function AdminPosts() {
  const postsRaw = await db.prepare(`
    SELECT Post.id, Post.title, Post.slug, Post.createdAt, Post.isPublished, Post.author, Post.views, Blog.name as blogName, Blog.domain as blogDomain
    FROM Post
    LEFT JOIN Blog ON Post.blogId = Blog.id
    ORDER BY Post.createdAt DESC
  `).all() as any[];

  // Formatação segura e serialização para Client Component
  const posts = postsRaw.map((p) => ({
    id: String(p.id),
    title: p.title || 'Sem título',
    slug: p.slug || '',
    createdAt: String(p.createdAt || ''),
    isPublished: Number(p.isPublished),
    author: p.author || 'Agente IA',
    views: Number(p.views || 0),
    blogName: p.blogName || 'Global',
    blogDomain: p.blogDomain || '',
  }));

  return <PostsClient initialPosts={posts} />;
}
