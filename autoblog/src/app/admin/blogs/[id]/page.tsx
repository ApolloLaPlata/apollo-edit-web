import React from 'react';
import db from '@/lib/db';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import ChatInterface from './ChatInterface';

export default async function BlogChatPage(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const blogRaw = db.prepare(`
    SELECT 
      Blog.*, 
      AgentConfig.id as agentConfig_id, 
      AgentConfig.isActive as agentConfig_isActive, 
      AgentConfig.postFrequency as agentConfig_postFrequency,
      AgentConfig.personaPrompt as agentConfig_personaPrompt
    FROM Blog
    LEFT JOIN AgentConfig ON AgentConfig.blogId = Blog.id
    WHERE Blog.id = ?
  `).get(params.id) as any;

  let blog = blogRaw ? {
    ...blogRaw,
    agentConfig: blogRaw.agentConfig_id ? {
      id: blogRaw.agentConfig_id,
      isActive: Boolean(blogRaw.agentConfig_isActive),
      postFrequency: Number(blogRaw.agentConfig_postFrequency || 0),
      personaPrompt: blogRaw.agentConfig_personaPrompt || ''
    } : null
  } as any : null;

  if (blog && !blog.agentConfig) {
    const crypto = require('crypto');
    const newConfigId = "cl" + crypto.randomUUID().replace(/-/g, "").substring(0, 23);
    const defaultPrompt = `Você é o Editor IA do portal ${blog.name}. Foco em clareza, SEO e engajamento no nicho de ${blog.niche}.`;
    const defaultImagePrompt = 'photorealistic, cinematic, highly detailed 8k';
    const now = new Date().toISOString();
    db.prepare('INSERT INTO AgentConfig (id, blogId, personaPrompt, imageStylePrompt, isActive, postFrequency, createdAt, updatedAt) VALUES (?, ?, ?, ?, 1, 3, ?, ?)').run(newConfigId, blog.id, defaultPrompt, defaultImagePrompt, now, now);
    blog.agentConfig = {
      id: newConfigId,
      isActive: true,
      postFrequency: 3,
      personaPrompt: defaultPrompt
    };
  }

  if (!blog) {
    notFound();
  }

  return (
    <div className="max-w-[1440px] mx-auto space-y-6 pb-16 animate-in fade-in duration-500 h-full flex flex-col">
      
      {/* HEADER EXECUTIVO DO CORTEX */}
      <div className="bg-gradient-to-b from-slate-900/90 to-slate-900/40 backdrop-blur-2xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6 shrink-0">
        <div className="absolute top-0 right-0 w-[350px] h-[350px] bg-gradient-to-bl from-blue-500/10 via-cyan-500/5 to-transparent rounded-full blur-3xl pointer-events-none -mr-28 -mt-28" />
        
        <div className="space-y-2 relative z-10">
          <div className="flex items-center gap-3">
            <Link
              href="/admin/blogs"
              className="p-2 rounded-xl bg-slate-950/80 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors border border-slate-800 text-xs font-bold"
              title="Voltar para a Frota de Veículos"
            >
              ← Frota
            </Link>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold tracking-wide">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
              CORTEX NEURAL • {blog.niche.toUpperCase()}
            </div>
          </div>

          <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <span>🧠</span>
            <span>Escritório Virtual: {blog.name}</span>
          </h1>
          <p className="text-slate-400 text-xs md:text-sm font-normal">
            Domínio: <span className="font-mono font-bold text-slate-300">{blog.domain}</span> • Comande e reconfigure a personalidade do Agente Executivo.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <div className="bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 flex items-center gap-4 text-xs font-bold text-slate-300 shadow-inner">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Ritmo de Edição</span>
              <span className="text-blue-400 font-mono">{blog.agentConfig?.postFrequency} posts/dia</span>
            </div>
            <div className="border-l border-slate-800 pl-4">
              <span className="text-slate-500 block text-[10px] uppercase">Status da IA</span>
              {blog.agentConfig?.isActive ? (
                <span className="text-emerald-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" /> Ativo
                </span>
              ) : (
                <span className="text-red-400">Pausado</span>
              )}
            </div>
          </div>

          <Link
            href={`/admin/appearance?blogId=${blog.id}`}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 hover:text-white transition-all border border-slate-700 text-xs font-bold flex items-center gap-2"
          >
            <span>🎨</span> Design
          </Link>

          <a
            href={`https://${blog.domain}`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white transition-all shadow-md shadow-blue-600/20 text-xs font-bold flex items-center gap-1.5"
          >
            <span>Vitrine ↗</span>
          </a>
        </div>
      </div>
      
      {/* CONSOLE DE CHAT DO CORTEX */}
      <ChatInterface blog={blog} agentConfig={blog.agentConfig} />
    </div>
  );
}
