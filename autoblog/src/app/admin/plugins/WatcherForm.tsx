'use client';

import { useState } from 'react';

export default function WatcherForm({ blogs }: { blogs: { id: string, name: string }[] }) {
  const [url, setUrl] = useState('');
  const [selectedBlog, setSelectedBlog] = useState(blogs[0]?.id || '');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url || !selectedBlog) return;

    setStatus('loading');
    setMessage('Iniciando o Watcher no background...');
    
    try {
      const res = await fetch(`/api/admin/blogs/${selectedBlog}/watch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ videoUrl: url })
      });
      const data = await res.json();
      
      if (data.success) {
        setStatus('success');
        setMessage(data.message);
        setUrl('');
      } else {
        setStatus('error');
        setMessage(data.error || 'Erro ao acionar o Watcher');
      }
    } catch (err) {
      setStatus('error');
      setMessage('Erro de conexão com o servidor.');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3">
      <div className="flex flex-col gap-1">
        <label className="text-xs text-slate-400 font-bold uppercase">Blog Alvo</label>
        <select 
          value={selectedBlog} 
          onChange={(e) => setSelectedBlog(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-red-500"
        >
          {blogs.map(b => (
            <option key={b.id} value={b.id}>{b.name}</option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs text-slate-400 font-bold uppercase">Link do YouTube</label>
        <input 
          type="url" 
          placeholder="https://youtube.com/watch?v=..." 
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          required
          className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-sm text-white focus:outline-none focus:border-red-500 placeholder-slate-600"
        />
      </div>
      <button 
        type="submit" 
        disabled={status === 'loading'}
        className="w-full bg-red-600 hover:bg-red-500 text-white font-bold py-2 rounded-lg text-sm transition-colors shadow-[0_0_15px_rgba(220,38,38,0.3)] disabled:opacity-50"
      >
        {status === 'loading' ? 'Espionando...' : 'Ativar Watcher'}
      </button>
      
      {message && (
        <p className={`text-xs mt-2 ${status === 'error' ? 'text-red-400' : 'text-green-400'}`}>
          {message}
        </p>
      )}
    </form>
  );
}
