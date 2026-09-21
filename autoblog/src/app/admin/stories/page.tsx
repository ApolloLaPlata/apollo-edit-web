import React from 'react';
import Link from 'next/link';
import db from '@/lib/db';

export const metadata = {
  title: 'Web Stories | CMS Admin',
  description: 'Gerenciador de Vídeos e Web Stories',
};

export default function AdminStoriesPage() {
  let stories = [];
  try {
    stories = db.prepare('SELECT WebStory.*, Blog.name as blogName FROM WebStory LEFT JOIN Blog ON WebStory.blogId = Blog.id ORDER BY WebStory.createdAt DESC LIMIT 50').all() as any[];
  } catch (error) {
    console.error("Erro ao puxar WebStories", error);
  }

  return (
    <div className="p-6 md:p-10 space-y-8 bg-slate-950 min-h-screen text-slate-200">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-black text-white tracking-tight flex items-center gap-3">
            <span className="text-theme-accent text-5xl">📱</span>
            Central de Stories
          </h1>
          <p className="text-slate-400 mt-2 text-sm font-medium">Controle de Mídias Curtas e Vídeos (Doom Scrolling Engine)</p>
        </div>
        <Link 
          href="/admin/stories/new" 
          className="bg-theme-accent hover:bg-theme-accent-hover text-black font-black uppercase tracking-widest text-xs px-6 py-3 rounded-lg shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all"
        >
          + Injetar Nova Story
        </Link>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900 border-b border-slate-800 text-[10px] uppercase tracking-widest text-slate-500 font-black">
                <th className="p-5">Capa</th>
                <th className="p-5">Título / Resumo</th>
                <th className="p-5">Franquia (Blog)</th>
                <th className="p-5">Data de Ingestão</th>
                <th className="p-5 text-right">Controles</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {stories.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-500 font-medium">
                    <div className="flex flex-col items-center">
                       <span className="text-4xl mb-4 opacity-50">📂</span>
                       Nenhuma Story foi carregada no banco de dados. 
                    </div>
                  </td>
                </tr>
              ) : (
                stories.map((story) => (
                  <tr key={story.id} className="hover:bg-slate-800/20 transition-colors group">
                    <td className="p-5 align-middle">
                      {story.imageUrl || story.videoUrl ? (
                         <div className="w-14 h-20 bg-slate-950 rounded border border-slate-700 overflow-hidden relative shadow-lg">
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img src={story.imageUrl || "https://images.pexels.com/photos/1040893/pexels-photo-1040893.jpeg?auto=compress&cs=tinysrgb&w=200"} alt="capa" className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity" />
                         </div>
                      ) : (
                         <div className="w-14 h-20 bg-slate-900 rounded border border-slate-800 flex items-center justify-center text-xs text-slate-600">N/A</div>
                      )}
                    </td>
                    <td className="p-5 align-middle">
                      <div className="font-bold text-white text-sm mb-1">{story.title}</div>
                      <div className="text-xs text-slate-400 line-clamp-1 max-w-sm">{story.content}</div>
                    </td>
                    <td className="p-5 align-middle text-xs font-semibold text-theme-accent">
                      {story.blogName || 'Global'}
                    </td>
                    <td className="p-5 align-middle text-xs text-slate-500 font-medium tracking-wide">
                      {new Date(story.createdAt).toLocaleString('pt-BR')}
                    </td>
                    <td className="p-5 align-middle text-right">
                      <button className="text-[10px] px-3 py-1.5 border border-slate-700 rounded text-slate-400 hover:text-white hover:border-slate-500 font-bold uppercase tracking-wider transition-colors mr-2">
                         Editar
                      </button>
                      <button className="text-[10px] px-3 py-1.5 border border-red-900/50 bg-red-950/20 rounded text-red-500 hover:text-white hover:bg-red-600 font-bold uppercase tracking-wider transition-colors">
                         Del
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
