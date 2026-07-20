import React, { useState, useEffect } from 'react';
import { Archive, Trash2, Copy, FileText, Play, Square, Loader2, Clock } from 'lucide-react';
import { SavedScript } from '../lib/gemini';
import ReactMarkdown from 'react-markdown';
import { toast } from './Toast';

export function History() {
  const [scripts, setScripts] = useState<SavedScript[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('scripts_history');
    if (saved) {
      try {
        setScripts(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to parse history', e);
      }
    }
    
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  const handlePlay = (id: string, text: string) => {
    if (isPlaying === id) {
      window.speechSynthesis.cancel();
      setIsPlaying(null);
      return;
    }

    window.speechSynthesis.cancel();
    // Remove markdown formatting for better speech
    const cleanText = text.replace(/[#*`_\[\]()]/g, '');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.1; // Slightly faster for scripts
    utterance.onend = () => setIsPlaying(null);
    window.speechSynthesis.speak(utterance);
    setIsPlaying(id);
  };

  const getReadingTime = (text: string) => {
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.ceil(words / 150);
    return `${minutes} min de leitura`;
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este roteiro do histórico?')) {
      const updated = scripts.filter(s => s.id !== id);
      setScripts(updated);
      localStorage.setItem('scripts_history', JSON.stringify(updated));
    }
  };

  const handleCopy = (content: string) => {
    navigator.clipboard.writeText(content);
    toast.success('Roteiro copiado para a área de transferência!');
  };

  const clearHistory = () => {
    if (window.confirm('Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.')) {
      setScripts([]);
      localStorage.removeItem('scripts_history');
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-zinc-900 flex items-center gap-2">
            <Archive className="text-indigo-600" />
            Arquivo de Roteiros
          </h2>
          <p className="text-zinc-500 mt-1">Acesse todos os roteiros gerados anteriormente.</p>
        </div>
        
        {scripts.length > 0 && (
          <button 
            onClick={clearHistory}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors"
          >
            <Trash2 size={16} />
            Limpar Histórico
          </button>
        )}
      </div>

      {scripts.length === 0 ? (
        <div className="bg-white border border-zinc-200 rounded-xl p-12 text-center flex flex-col items-center justify-center">
          <Archive size={48} className="text-zinc-300 mb-4" />
          <h3 className="text-lg font-medium text-zinc-900 mb-1">Nenhum roteiro salvo</h3>
          <p className="text-zinc-500">Os roteiros que você gerar aparecerão aqui automaticamente.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {scripts.map((script) => (
            <div key={script.id} className="bg-white border border-zinc-200 rounded-xl overflow-hidden shadow-sm">
              <div 
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-zinc-50 transition-colors"
                onClick={() => setExpandedId(expandedId === script.id ? null : script.id)}
              >
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${script.type === 'shorts' ? 'bg-orange-100 text-orange-600' : 'bg-indigo-100 text-indigo-600'}`}>
                    <FileText size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-zinc-900">{script.title || 'Roteiro sem título'}</h3>
                    <div className="flex items-center gap-3 text-sm text-zinc-500 mt-1">
                      <span>{new Date(script.date).toLocaleString('pt-BR')}</span>
                      <span className="w-1 h-1 rounded-full bg-zinc-300"></span>
                      <span className="capitalize">{script.type === 'shorts' ? 'Vídeo Curto (Shorts/TikTok)' : 'Vídeo Longo (YouTube)'}</span>
                      <span className="w-1 h-1 rounded-full bg-zinc-300"></span>
                      <span className="flex items-center gap-1"><Clock size={12} /> {getReadingTime(script.content)}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              {expandedId === script.id && (
                <div className="border-t border-zinc-100 p-4 bg-zinc-50">
                  <div className="flex justify-end gap-2 mb-4">
                    <button 
                      onClick={() => handlePlay(script.id, script.content)}
                      className={`flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${isPlaying === script.id ? 'bg-indigo-100 text-indigo-700 border border-indigo-200' : 'bg-white text-zinc-700 border border-zinc-200 hover:bg-zinc-50'}`}
                    >
                      {isPlaying === script.id ? <><Square size={14} /> Parar Áudio</> : <><Play size={14} /> Ouvir Roteiro</>}
                    </button>
                    <button 
                      onClick={() => handleCopy(script.content)}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-zinc-700 bg-white border border-zinc-200 hover:bg-zinc-50 rounded-md transition-colors"
                    >
                      <Copy size={14} /> Copiar
                    </button>
                    <button 
                      onClick={() => handleDelete(script.id)}
                      className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-red-600 bg-white border border-red-200 hover:bg-red-50 rounded-md transition-colors"
                    >
                      <Trash2 size={14} /> Excluir
                    </button>
                  </div>
                  <div className="prose prose-sm max-w-none bg-white p-4 rounded-lg border border-zinc-200">
                    <ReactMarkdown>{script.content}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
