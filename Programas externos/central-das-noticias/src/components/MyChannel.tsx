import React, { useState } from 'react';
import { Bookmark, Clock, BookmarkCheck, Monitor, Youtube, Loader2, FileText, Sparkles, TrendingUp, ThumbsUp, MessageSquare, Share2, ExternalLink, Bot, PenTool, Target, X } from 'lucide-react';
import { VideoAnalysisData, analyzeChannelVideos } from '../lib/gemini';
import ReactMarkdown from 'react-markdown';

interface MyChannelProps {
  savedVideos: any[];
  handleToggleSaveVideo: (video: any) => void;
  videoAnalysis: Record<string, VideoAnalysisData>;
  isAnalyzingVideo: Record<string, boolean>;
  handleAnalyzeVideo: (video: any) => void;
  isGeneratingVideoScript: Record<string, boolean>;
  handleGenerateVideoScript: (video: any) => void;
}

export function MyChannel({
  savedVideos,
  handleToggleSaveVideo,
  videoAnalysis,
  isAnalyzingVideo,
  handleAnalyzeVideo,
  isGeneratingVideoScript,
  handleGenerateVideoScript
}: MyChannelProps) {
  const [isAnalyzingChannel, setIsAnalyzingChannel] = useState(false);
  const [channelAnalysis, setChannelAnalysis] = useState<string | null>(null);
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);

  const handleAnalyzeChannel = async () => {
    setIsAnalyzingChannel(true);
    try {
      const result = await analyzeChannelVideos(savedVideos);
      setChannelAnalysis(result);
    } catch (error) {
      console.error("Failed to analyze channel:", error);
      setChannelAnalysis("Houve um erro ao analisar o canal. Tente novamente.");
    } finally {
      setIsAnalyzingChannel(false);
    }
  };

  const formatNumber = (num?: number) => {
    if (num === undefined || num === null) return 'N/A';
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (savedVideos.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-zinc-400 border-2 border-dashed border-zinc-800 rounded-xl bg-transparent/50">
        <Bookmark size={48} className="mb-4 opacity-50" />
        <p className="text-lg font-medium text-zinc-400">Nenhum vídeo salvo ainda</p>
        <p className="text-sm mt-1">Busque por vídeos na aba "Mineração Viral" e clique no ícone de salvar para guardá-los aqui.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-zinc-100 flex items-center gap-2">
          <Youtube size={24} className="text-red-600" />
          Meu Canal
        </h2>
        <div className="flex items-center gap-3">
          <button
            onClick={handleAnalyzeChannel}
            disabled={isAnalyzingChannel || savedVideos.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isAnalyzingChannel ? <Loader2 size={18} className="animate-spin" /> : <Target size={18} />}
            Analisar Canal & Sugerir Temas
          </button>
          <div className="text-sm text-zinc-400 font-medium bg-zinc-800 px-3 py-1 rounded-full">
            {savedVideos.length} {savedVideos.length === 1 ? 'vídeo salvo' : 'vídeos salvos'}
          </div>
        </div>
      </div>

      {channelAnalysis && (
        <div className="bg-indigo-900/30 border border-indigo-100 rounded-xl p-6 animate-in fade-in slide-in-from-top-4">
          <div className="flex items-center gap-2 mb-4 text-indigo-800">
            <Bot size={24} />
            <h3 className="text-xl font-bold">Análise Estratégica do Canal</h3>
          </div>
          <div className="prose prose-indigo max-w-none prose-sm sm:prose-base">
            <ReactMarkdown>{channelAnalysis}</ReactMarkdown>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {savedVideos.map((video, index) => {
          const isSaved = true; // They are all saved in this view
          return (
            <div key={index} className="bg-zinc-900 rounded-xl border border-zinc-800 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
              <div className="relative aspect-video bg-zinc-800">
                <img src={video.thumbnail} alt={video.title} className="w-full h-full object-cover" />
                <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs font-bold px-2 py-1 rounded flex items-center gap-1">
                  <Clock size={12} />
                  {video.duration || 'N/A'}
                </div>
                <button
                  onClick={() => handleToggleSaveVideo(video)}
                  className={`absolute top-2 right-2 p-2 rounded-full backdrop-blur-sm transition-colors shadow-sm ${isSaved ? 'bg-red-600 text-white hover:bg-red-700' : 'bg-black/50 text-white hover:bg-black/70'}`}
                  title={isSaved ? "Remover dos salvos" : "Salvar ideia"}
                >
                  {isSaved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
                </button>
              </div>
              <div className="p-4 flex-1 flex flex-col">
                <h3 className="font-bold text-zinc-100 mb-1 line-clamp-2 leading-snug" title={video.title}>{video.title}</h3>
                <div className="flex items-center gap-2 mb-3 text-xs text-zinc-400">
                  <span className="font-medium text-zinc-700">{video.author}</span>
                  <span>•</span>
                  <span>{video.ago}</span>
                </div>
                
                <div className="grid grid-cols-4 gap-2 mb-4 text-xs text-zinc-400 bg-transparent p-2 rounded-lg border border-zinc-100">
                  <div className="flex flex-col items-center justify-center text-center" title="Visualizações">
                    <Monitor size={14} className="mb-1 text-zinc-400" />
                    <span className="font-semibold text-zinc-700">{formatNumber(video.views)}</span>
                  </div>
                  <div className="flex flex-col items-center justify-center text-center" title="Curtidas (Estimativa)">
                    <ThumbsUp size={14} className="mb-1 text-zinc-400" />
                    <span className="font-semibold text-zinc-700">{formatNumber(video.likes)}</span>
                  </div>
                  <div className="flex flex-col items-center justify-center text-center" title="Comentários (Estimativa)">
                    <MessageSquare size={14} className="mb-1 text-zinc-400" />
                    <span className="font-semibold text-zinc-700">{formatNumber(video.comments)}</span>
                  </div>
                  <div className="flex flex-col items-center justify-center text-center" title="Compartilhamentos (Estimativa)">
                    <Share2 size={14} className="mb-1 text-zinc-400" />
                    <span className="font-semibold text-zinc-700">{formatNumber(video.shares)}</span>
                  </div>
                </div>

                <p className="text-sm text-zinc-400 line-clamp-2 mb-4 flex-1">{video.description}</p>
                
                <div className="mt-auto pt-4 border-t border-zinc-100 space-y-3">
                  <div className="flex gap-2">
                    <button 
                      onClick={() => handleAnalyzeVideo(video)}
                      disabled={isAnalyzingVideo[video.url]}
                      className="flex-1 bg-red-900/30 hover:bg-red-100 text-red-400 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                    >
                      {isAnalyzingVideo[video.url] ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                      Analisar com IA
                    </button>
                    <button 
                      onClick={() => handleGenerateVideoScript(video)}
                      disabled={isGeneratingVideoScript[video.url]}
                      className="flex-1 bg-zinc-900 hover:bg-zinc-800 text-white py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
                      title="Gerar roteiro baseado neste vídeo"
                    >
                      {isGeneratingVideoScript[video.url] ? <Loader2 size={16} className="animate-spin" /> : <PenTool size={16} />}
                      Criar Roteiro
                    </button>
                    <button 
                      onClick={() => setPlayingVideoUrl(video.url)}
                      className="p-2 bg-transparent hover:bg-zinc-800 text-zinc-400 rounded-md transition-colors"
                      title="Assistir no App"
                    >
                      <ExternalLink size={16} />
                    </button>
                  </div>
                  
                  {videoAnalysis[video.url] && (
                    <div className="bg-red-900/30/50 rounded-lg p-4 text-sm text-zinc-700 border border-red-100 animate-in fade-in slide-in-from-top-2 space-y-4">
                      <div className="font-bold text-red-900 flex items-center gap-1 border-b border-red-200 pb-2">
                        <Bot size={16} /> Análise de Dados do Vídeo
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Sentimento</span>
                          <span className="bg-zinc-900 px-2 py-1 rounded border border-zinc-800 inline-block">{videoAnalysis[video.url].sentiment}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Público-Alvo</span>
                          <span className="bg-zinc-900 px-2 py-1 rounded border border-zinc-800 inline-block">{videoAnalysis[video.url].targetAudience}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Apelo Emocional</span>
                          <span className="bg-zinc-900 px-2 py-1 rounded border border-zinc-800 inline-block">{videoAnalysis[video.url].emotionalAppeal}</span>
                        </div>
                        <div>
                          <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Controvérsia</span>
                          <span className="bg-zinc-900 px-2 py-1 rounded border border-zinc-800 inline-block">{videoAnalysis[video.url].controversyLevel}</span>
                        </div>
                      </div>

                      <div>
                        <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Ganchos Principais</span>
                        <ul className="list-disc pl-4 space-y-1">
                          {videoAnalysis[video.url].keyHooks.map((hook, i) => <li key={i}>{hook}</li>)}
                        </ul>
                      </div>

                      <div>
                        <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Fatores de Viralização</span>
                        <ul className="list-disc pl-4 space-y-1">
                          {videoAnalysis[video.url].viralFactors.map((factor, i) => <li key={i}>{factor}</li>)}
                        </ul>
                      </div>

                      <div>
                        <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Pontos para Checagem (Fact-Check)</span>
                        <ul className="list-disc pl-4 space-y-1">
                          {videoAnalysis[video.url].factCheckPoints.map((point, i) => <li key={i}>{point}</li>)}
                        </ul>
                      </div>

                      <div className="bg-zinc-900 p-3 rounded border border-zinc-800">
                        <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">Ideias de Títulos para o seu Canal</span>
                        <ul className="list-disc pl-4 space-y-1 font-medium text-red-400">
                          {videoAnalysis[video.url].suggestedTitles.map((title, i) => <li key={i}>{title}</li>)}
                        </ul>
                      </div>

                      <div>
                        <span className="font-semibold text-zinc-100 block text-xs uppercase tracking-wider mb-1">O que faltou falar (Gaps)</span>
                        <p className="bg-zinc-900 p-2 rounded border border-zinc-800">{videoAnalysis[video.url].contentGaps}</p>
                      </div>

                      <div className="bg-zinc-900 text-white p-3 rounded-lg">
                        <span className="font-semibold text-zinc-300 block text-xs uppercase tracking-wider mb-1">Veredito Final</span>
                        <p>{videoAnalysis[video.url].overallVerdict}</p>
                      </div>

                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

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
