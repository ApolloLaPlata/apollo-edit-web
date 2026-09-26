import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import PostEditForm from './PostEditForm';

export default async function AdminPostEdit(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const post = await db.prepare(`SELECT * FROM Post WHERE id = ?`).get(params.id) as any;
  const categories = await db.prepare(`SELECT * FROM Category WHERE blogId = ?`).all(post?.blogId);
  const socialSnippets = await db.prepare(`SELECT * FROM SocialSnippet WHERE postId = ?`).all(params.id) as any[];

  if (!post) {
    notFound();
  }

  return (
    <main className="flex min-h-screen flex-col bg-slate-950 text-slate-200 font-sans p-8">
      <div className="max-w-4xl mx-auto w-full">
        <div className="mb-8 border-b border-slate-800 pb-4">
          <h1 className="text-3xl font-bold text-white tracking-tight">Editar Artigo</h1>
          <p className="text-slate-400 mt-1">ID: {post.id}</p>
        </div>
        <PostEditForm initialData={post} categories={categories} socialSnippets={socialSnippets} />
      </div>
    </main>
  );
}
