import React, { useState, useEffect } from 'react';
import { Youtube, Loader2, TrendingUp, Clock, ExternalLink, ThumbsUp, MessageCircle, Share2, X } from 'lucide-react';

type VideoResult = {
  title: string;
  url: string;
  thumbnail: string;
  author: string;
  views: number;
  ago: string;
  duration: string;
  likes?: number;
  comments?: number;
  shares?: number;
};

const CATEGORIES = [
  { id: 'politica', label: 'Política Nacional', query: 'notícias política brasil hoje' },
  { id: 'economia', label: 'Economia', query: 'notícias economia brasil mercado' },
  { id: 'mundo', label: 'Internacional', query: 'notícias internacionais hoje' },
  { id: 'polemicas', label: 'Polêmicas e Debates', query: 'debate polêmica podcast brasil' }
];

export function RadarYouTube() {
  const [activeCategory, setActiveCategory] = useState(CATEGORIES[0]);
  const [videos, setVideos] = useState<VideoResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    fetchVideos(activeCategory.query);
  }, [activeCategory]);

  const fetchVideos = async (query: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/search-youtube?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error('Falha ao buscar vídeos');
      const data = await res.json();
      setVideos(data.videos || []);
    } catch (err: any) {
      console.error(err);
      setError('Não foi possível carregar os vídeos em alta no momento.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatViews = (views: number) => {
    if (views >= 1000000) return `${(views / 1000000).toFixed(1)}M`;
    if (views >= 1000) return `${(views / 1000).toFixed(1)}K`;
    return views.toString();
  };

  return (
    <div className="space-y-6">
      <div className="bg-zinc-900 rounded-xl shadow-sm border border-zinc-800 p-6">
        <h2 className="text-2xl font-bold text-zinc-100 mb-2 flex items-center gap-2">
          <TrendingUp className="text-red-600" size={28} />
          Radar YouTube (Em Alta)
        </h2>
        <p className="text-zinc-400 mb-6">
          Acompanhe os vídeos que estão bombando no momento. Escolha uma categoria para ver o que está em destaque na plataforma.
        </p>
        
        <div className="flex flex-wrap gap-2">
          {CATEGORIES.map(category => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                activeCategory.id === category.id
                  ? 'bg-red-600 text-white shadow-sm'
                  : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-200'
              }`}
            >
              {category.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-zinc-400">
          <Loader2 size={40} className="animate-spin mb-4 text-red-600" />
          <p className="text-lg">Buscando vídeos em alta...</p>
        </div>
      ) : error ? (
        <div className="bg-red-900/30 text-red-600 p-6 rounded-xl text-center border border-red-100">
          <p>{error}</p>
          <button 
            onClick={() => fetchVideos(activeCategory.query)}
            className="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 rounded-md font-medium transition-colors"
          >
            Tentar Novamente
          </button>
        </div>
      ) : videos.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video, index) => (
            <div key={index} className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
              <div className="relative aspect-video bg-zinc-800">
                <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover" />
                <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs font-bold px-2 py-1 rounded flex items-center gap-1">
                  <Clock size={12} />
                  {video.duration || 'N/A'}
                </div>
              </div>
              <div className="p-4 flex-1 flex flex-col">
                <h3 className="font-bold text-zinc-100 mb-1 line-clamp-2 leading-snug" title={video.title}>{video.title}</h3>
                <div className="flex items-center gap-2 mb-3 text-xs text-zinc-400">
                  <span className="font-medium text-zinc-700">{video.author}</span>
                  <span>•</span>
                  <span>{video.ago}</span>
                </div>
                <div className="flex items-center gap-4 mb-4 text-xs text-zinc-400">
                  <div className="flex items-center gap-1" title="Visualizações">
                    <Youtube size={14} className="text-zinc-400" />
                    <span className="font-medium text-zinc-700">{formatViews(video.views)}</span>
                  </div>
                  {video.likes !== undefined && (
                    <div className="flex items-center gap-1" title="Curtidas">
                      <ThumbsUp size={14} className="text-zinc-400" />
                      <span className="font-medium text-zinc-700">{formatViews(video.likes)}</span>
                    </div>
                  )}
                  {video.comments !== undefined && (
                    <div className="flex items-center gap-1" title="Comentários">
                      <MessageCircle size={14} className="text-zinc-400" />
                      <span className="font-medium text-zinc-700">{formatViews(video.comments)}</span>
                    </div>
                  )}
                  {video.shares !== undefined && (
                    <div className="flex items-center gap-1" title="Compartilhamentos">
                      <Share2 size={14} className="text-zinc-400" />
                      <span className="font-medium text-zinc-700">{formatViews(video.shares)}</span>
                    </div>
                  )}
                </div>
                <div className="mt-auto pt-3 border-t border-zinc-800 flex items-center justify-between">
                  <button 
                    onClick={() => (window as any).addToTransferArea?.('video', video.title, video.author, video.thumbnail)}
                    className="px-2 py-1 bg-indigo-900/30 text-indigo-400 text-xs rounded hover:bg-indigo-800/40 transition-colors flex items-center gap-1 font-medium border border-indigo-500/20"
                    title="Enviar para Área de Transferência"
                  >
                    <span>🎒 Enviar para HUD</span>
                  </button>
                  <button 
                    onClick={() => setPlayingVideoUrl(video.url)}
                    className="p-2 bg-red-900/30 hover:bg-red-800/50 text-red-500 rounded-md transition-colors"
                    title="Assistir no App"
                  >
                    <ExternalLink size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-20 text-zinc-400 bg-zinc-900 rounded-xl border border-zinc-800">
          <Youtube size={48} className="mx-auto mb-4 text-zinc-300" />
          <p className="text-lg">Nenhum vídeo encontrado para esta categoria.</p>
        </div>
      )}

      {/* Video Player Modal */}
      {playingVideoUrl && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-zinc-900 rounded-xl overflow-hidden w-full max-w-5xl shadow-2xl border border-zinc-800 flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-zinc-800">
              <h3 className="text-white font-medium flex items-center gap-2">
                <Youtube size={20} className="text-red-500" />
                Reprodutor de Vídeo
              </h3>
              <button 
                onClick={() => setPlayingVideoUrl(null)}
                className="text-zinc-400 hover:text-white p-1 rounded-md hover:bg-zinc-800 transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            <div className="relative w-full aspect-video bg-black">
              <iframe
                src={`https://www.youtube.com/embed/${playingVideoUrl.split('v=')[1]?.split('&')[0] || playingVideoUrl.split('youtu.be/')[1]?.split('?')[0]}?autoplay=1`}
                title="YouTube video player"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="absolute inset-0 w-full h-full border-0"
              ></iframe>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
