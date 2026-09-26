import React from 'react';
import db from '@/lib/db';
import BlogsClient from './BlogsClient';

export default async function BlogsManager() {
  const blogsRaw = await db.prepare(`
    SELECT 
      Blog.*, 
      AgentConfig.id as agentConfig_id, 
      AgentConfig.isActive as agentConfig_isActive, 
      AgentConfig.postFrequency as agentConfig_postFrequency,
      (SELECT COUNT(*) FROM Post WHERE Post.blogId = Blog.id) as posts_count
    FROM Blog
    LEFT JOIN AgentConfig ON AgentConfig.blogId = Blog.id
    ORDER BY Blog.createdAt DESC
  `).all() as any[];

  // Formatação segura para serialização no Client Component
  const blogs = blogsRaw.map((b) => ({
    id: String(b.id),
    name: b.name || 'Portal sem nome',
    domain: b.domain || '',
    niche: b.niche || 'Geral',
    description: b.description || '',
    theme: b.theme || 'dark',
    agentConfig: b.agentConfig_id ? {
      id: String(b.agentConfig_id),
      isActive: Boolean(b.agentConfig_isActive),
      postFrequency: Number(b.agentConfig_postFrequency || 0),
    } : null,
    _count: { posts: Number(b.posts_count || 0) },
  }));

  return <BlogsClient initialBlogs={blogs} />;
}
