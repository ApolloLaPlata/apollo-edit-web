import React from 'react';
import db from '@/lib/db';
import { redirect } from 'next/navigation';
import { revalidatePath } from 'next/cache';
import crypto from 'crypto';

export default async function AdminSources() {
  const blogs = await db.prepare('SELECT id, name FROM Blog').all() as {id: string, name: string}[];
  const sources = await db.prepare(`
    SELECT ContentSource.*, Blog.name as blogName 
    FROM ContentSource 
    JOIN Blog ON ContentSource.blogId = Blog.id
    ORDER BY ContentSource.createdAt DESC
  `).all() as any[];

  async function handleAddSource(formData: FormData) {
    'use server';
    const blogId = formData.get('blogId') as string;
    const name = formData.get('name') as string;
    const rssUrl = formData.get('rssUrl') as string;
    const niche = formData.get('niche') as string;

    if (!blogId || !name || !rssUrl) return;

    await db.prepare(`
      INSERT INTO ContentSource (id, blogId, name, rssUrl, niche)
      VALUES (?, ?, ?, ?, ?)
    `).run(crypto.randomUUID(), blogId, name, rssUrl, niche || 'geral');

    revalidatePath('/admin/sources');
  }

  async function handleDeleteSource(formData: FormData) {
    'use server';
    const id = formData.get('id') as string;
    await db.prepare('DELETE FROM ContentSource WHERE id = ?').run(id);
    revalidatePath('/admin/sources');
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-4xl font-black text-white flex items-center gap-3">
            <span className="text-cyan-400">🕷️</span> Spider Web
          </h1>
          <p className="text-slate-400 mt-2">Gerencie as fontes RSS de onde a IA extrai notícias para os Portais.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* ADD NEW SOURCE FORM */}
        <div className="bg-[#0b0b14] border border-[#1a1a2e] rounded-3xl p-6 shadow-2xl h-fit">
          <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">Adicionar Nova Fonte</h2>
          
          <form action={handleAddSource} className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Portal Destino</label>
              <select name="blogId" required className="w-full bg-[#151525] border border-white/5 rounded-xl p-3 text-white outline-none focus:border-cyan-500 transition-all">
                {blogs.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Nome da Fonte</label>
              <input type="text" name="name" placeholder="Ex: G1 Tecnologia" required className="w-full bg-[#151525] border border-white/5 rounded-xl p-3 text-white outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">URL (RSS Feed)</label>
              <input type="url" name="rssUrl" placeholder="https://..." required className="w-full bg-[#151525] border border-white/5 rounded-xl p-3 text-white outline-none focus:border-cyan-500" />
            </div>
            <div>
              <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Nicho Secundário</label>
              <input type="text" name="niche" placeholder="Ex: cripto, politica" className="w-full bg-[#151525] border border-white/5 rounded-xl p-3 text-white outline-none focus:border-cyan-500" />
            </div>
            
            <button type="submit" className="w-full mt-4 bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-black py-4 rounded-xl hover:scale-[1.02] transition-transform shadow-[0_0_20px_rgba(6,182,212,0.3)]">
              + INJETAR FONTE NO MOTOR
            </button>
          </form>
        </div>

        {/* LIST OF SOURCES */}
        <div className="lg:col-span-2">
          <div className="bg-[#0b0b14] border border-[#1a1a2e] rounded-3xl p-6 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-6 border-b border-white/10 pb-4">Sensores Ativos ({sources.length})</h2>
            
            <div className="space-y-4">
              {sources.length === 0 && (
                <div className="text-center p-10 border border-dashed border-white/10 rounded-2xl text-slate-500">
                  Nenhuma fonte conectada. O motor autônomo usará o Google Trends como Fallback.
                </div>
              )}
              {sources.map(src => (
                <div key={src.id} className="flex flex-col sm:flex-row justify-between items-start sm:items-center p-5 bg-[#151525] border border-white/5 rounded-2xl gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-1">
                      <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                      <h3 className="font-bold text-white text-lg">{src.name}</h3>
                      <span className="text-[10px] bg-cyan-950 text-cyan-400 px-2 py-0.5 rounded border border-cyan-900/50 uppercase tracking-wider">{src.blogName}</span>
                    </div>
                    <p className="text-slate-400 text-xs font-mono">{src.rssUrl}</p>
                  </div>
                  
                  <form action={handleDeleteSource}>
                    <input type="hidden" name="id" value={src.id} />
                    <button type="submit" className="text-red-500/70 hover:text-red-400 hover:bg-red-500/10 p-2 rounded-lg transition-colors font-bold text-xs uppercase tracking-widest border border-transparent hover:border-red-500/20">
                      Desconectar
                    </button>
                  </form>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
