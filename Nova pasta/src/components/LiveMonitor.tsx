import React, { useState } from 'react';
import { Activity, Users, Heart, Video, Play, Loader2, AlertCircle, ExternalLink, Eye, Calendar, RefreshCw, Maximize2, X, Database, Link as LinkIcon, Settings as SettingsIcon } from 'lucide-react';
import { Type } from '@google/genai';
import { executeWithRetry } from '../lib/gemini';
import { scrapeWithApify } from '../lib/apify';

interface RecentVideo {
  title: string;
  views: string;
  likes: string;
  date?: string;
}

interface MonitorData {
  followers: string;
  likes: string;
  videos: string;
  username: string;
  recentVideos: RecentVideo[];
}

export function LiveMonitor() {
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [baseData, setBaseData] = useState<MonitorData | null>(null);
  const [showAllVideos, setShowAllVideos] = useState(false);

  const handleStartMonitoring = async () => {
    if (!url.trim()) {
      setError('Por favor, insira o link da sua página (ex: Kwai, TikTok).');
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setBaseData(null);
    setStatusMsg('Iniciando análise...');

    try {
      const apifyKey = localStorage.getItem('api_key_apify');
      let pageContent = '';
      
      if (apifyKey && apifyKey.trim().length > 0) {
        setStatusMsg('Extraindo dados avançados com Apify (isso pode levar cerca de 15 a 30 segundos, ignorando bloqueios de JS)...');
        try {
          pageContent = await scrapeWithApify(url, apifyKey);
          setStatusMsg('Dados extraídos! Analisando conteúdo com IA...');
        } catch (apifyErr) {
          console.error("Apify scraping failed, falling back to basic Gemini:", apifyErr);
          // Falhou no Apify, vai seguir para o Gemini tentar ler
          setStatusMsg('Extração avançada falhou, tentando leitura básica...');
        }
      } else {
        setStatusMsg('Lendo URL com Gemini de forma básica...');
      }

      const hasExternalContent = pageContent.length > 0;
      
      let prompt = `Extraia SOMENTE os dados reais e públicos referentes à página solicitada.
      É EXTREMAMENTE IMPORTANTE: NÃO invente, NÃO simule, NÃO adivinhe e NÃO estime nenhum dado. Se você não conseguir ler a página ou se um dado não estiver disponível no texto da página, retorne "N/A".
      Se você não conseguir encontrar a lista de vídeos na página, retorne um array vazio [] para recentVideos. NUNCA invente títulos de vídeos.
      
      Extraia:
      1. Nome de usuário
      2. Número de seguidores
      3. Número total de curtidas
      4. Número total de vídeos (se visível)
      5. Uma lista de ATÉ 15 vídeos mais recentes visíveis na página (título exato, visualizações, curtidas, data se houver). Tente extrair o máximo possível, pelo menos 10 se estiverem visíveis.
      
      `;

      if (hasExternalContent) {
        prompt += `DADOS DA PÁGINA EXTRAÍDOS VIA ALGORITMO (EM MARKDOWN/TEXTO):\n\n${pageContent.substring(0, 50000)}`; // Limita o tamanho do texto
      } else {
        prompt += `Você DEVE usar a ferramenta urlContext para acessar a URL fornecida e ler o conteúdo real da página.\nURL para acessar: ${url}`;
      }

      const response = await executeWithRetry((ai) => ai.models.generateContent({
        model: 'gemini-3.1-pro-preview', // Switch to a better model for extraction
        contents: prompt,
        config: {
          tools: hasExternalContent ? [] : [{ urlContext: {} }],
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              username: { type: Type.STRING, description: 'Nome de usuário real extraído da página' },
              followers: { type: Type.STRING, description: 'Número real de seguidores (ex: 1.2M, 500K)' },
              likes: { type: Type.STRING, description: 'Número real total de curtidas' },
              videos: { type: Type.STRING, description: 'Número real total de vídeos' },
              recentVideos: {
                type: Type.ARRAY,
                description: 'Lista de vídeos recentes reais encontrados na página',
                items: {
                  type: Type.OBJECT,
                  properties: {
                    title: { type: Type.STRING, description: 'Título ou descrição do vídeo' },
                    views: { type: Type.STRING, description: 'Número de visualizações' },
                    likes: { type: Type.STRING, description: 'Número de curtidas' },
                    date: { type: Type.STRING, description: 'Data de publicação (se disponível)' }
                  },
                  required: ['title', 'views']
                }
              }
            },
            required: ['username', 'followers', 'likes', 'videos', 'recentVideos']
          }
        }
      }));

      const text = response.text;
      if (!text) throw new Error('Resposta vazia da IA');
      
      const data = JSON.parse(text) as MonitorData;
      setBaseData(data);
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Erro ao analisar a página. Verifique a URL e tente novamente.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const displayedVideos = baseData?.recentVideos ? (showAllVideos ? baseData.recentVideos : baseData.recentVideos.slice(0, 15)) : [];
  const hasMoreVideos = baseData?.recentVideos && baseData.recentVideos.length > 15;

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="bg-emerald-100 p-2 rounded-lg text-emerald-600">
              <Activity size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-zinc-900">Painel de Análise</h2>
              <p className="text-sm text-zinc-500">Extraia e cruze dados reais da sua página.</p>
            </div>
          </div>
          {baseData && (
            <button
              onClick={handleStartMonitoring}
              disabled={isAnalyzing}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-zinc-700 bg-zinc-100 hover:bg-zinc-200 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw size={16} className={isAnalyzing ? "animate-spin" : ""} />
              Atualizar Dados
            </button>
          )}
        </div>

        <div className="flex gap-3">
          <div className="relative flex-1">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Cole o link do seu perfil (ex: https://www.kwai.com/@descarganews)"
              className="w-full pl-4 pr-4 py-3 bg-zinc-50 border border-zinc-200 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all text-zinc-900 placeholder-zinc-400"
              disabled={isAnalyzing}
            />
          </div>
          {!baseData && (
            <button
              onClick={handleStartMonitoring}
              disabled={isAnalyzing || !url.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
            >
              {isAnalyzing ? (
                <div className="flex items-center gap-2 max-w-[200px] overflow-hidden">
                  <Loader2 size={20} className="animate-spin shrink-0" />
                  <span className="truncate text-sm" title={statusMsg || 'Extraindo Dados...'}>
                    {statusMsg || 'Extraindo Dados...'}
                  </span>
                </div>
              ) : (
                <>
                  <Play size={20} />
                  Analisar Perfil
                </>
              )}
            </button>
          )}
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-start gap-3 border border-red-100">
            <AlertCircle size={20} className="shrink-0 mt-0.5" />
            <p className="text-sm">{error}</p>
          </div>
        )}
      </div>

      {baseData && (
        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
          
          {/* API Integration Status (Modular Concept) */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-5 rounded-xl border border-zinc-200 shadow-sm flex items-start gap-4">
              <div className="bg-blue-50 p-3 rounded-lg text-blue-600 mt-1">
                <LinkIcon size={20} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-zinc-900">Fonte: Web Scraping</h3>
                  <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-bold rounded-full">Ativo</span>
                </div>
                <p className="text-sm text-zinc-500 mb-2">Dados extraídos diretamente da URL pública fornecida.</p>
                <div className="text-xs text-zinc-400 bg-zinc-50 p-2 rounded border border-zinc-100">
                  URL: {url}
                </div>
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-zinc-200 shadow-sm flex items-start gap-4 opacity-75">
              <div className="bg-purple-50 p-3 rounded-lg text-purple-600 mt-1">
                <Database size={20} />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <h3 className="font-bold text-zinc-900">Fonte: API Oficial</h3>
                  <span className="px-2 py-1 bg-zinc-100 text-zinc-600 text-xs font-bold rounded-full">Aguardando Configuração</span>
                </div>
                <p className="text-sm text-zinc-500 mb-2">Conecte as APIs (YouTube, TikTok) nas Configurações para cruzar dados oficiais com a leitura da página.</p>
                <button className="text-xs font-medium text-emerald-600 hover:text-emerald-700">
                  Configurar Integrações &rarr;
                </button>
              </div>
            </div>
          </div>

          {/* Top Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-5 rounded-xl border border-zinc-200 shadow-sm flex items-center gap-4 hover:border-emerald-200 transition-colors cursor-default">
              <div className="bg-indigo-50 p-3 rounded-lg text-indigo-600">
                <Users size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-500">Seguidores</p>
                <p className="text-2xl font-bold text-zinc-900">{baseData.followers}</p>
              </div>
            </div>
            
            <div className="bg-white p-5 rounded-xl border border-zinc-200 shadow-sm flex items-center gap-4 hover:border-emerald-200 transition-colors cursor-default">
              <div className="bg-pink-50 p-3 rounded-lg text-pink-600">
                <Heart size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-500">Curtidas Totais</p>
                <p className="text-2xl font-bold text-zinc-900">{baseData.likes}</p>
              </div>
            </div>

            <div className="bg-white p-5 rounded-xl border border-zinc-200 shadow-sm flex items-center gap-4 hover:border-emerald-200 transition-colors cursor-default">
              <div className="bg-orange-50 p-3 rounded-lg text-orange-600">
                <Video size={24} />
              </div>
              <div>
                <p className="text-sm font-medium text-zinc-500">Vídeos Publicados</p>
                <p className="text-2xl font-bold text-zinc-900">{baseData.videos}</p>
              </div>
            </div>
          </div>

          {/* Recent Videos */}
          <div className="bg-white p-6 rounded-xl border border-zinc-200 shadow-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-zinc-900">Vídeos Recentes (Extraídos da Página)</h3>
              <span className="text-sm font-medium text-zinc-500 bg-zinc-100 px-3 py-1 rounded-full">
                {baseData.recentVideos?.length || 0} encontrados
              </span>
            </div>
            
            {baseData.recentVideos && baseData.recentVideos.length > 0 ? (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {displayedVideos.map((video, index) => (
                    <div key={index} className="border border-zinc-100 rounded-lg p-4 hover:border-emerald-200 transition-colors bg-zinc-50">
                      <p className="font-medium text-zinc-900 mb-3 line-clamp-2" title={video.title}>
                        {video.title || 'Sem título'}
                      </p>
                      <div className="flex flex-wrap items-center gap-3 text-sm text-zinc-600">
                        {video.views && video.views !== 'N/A' && (
                          <div className="flex items-center gap-1">
                            <Eye size={16} className="text-zinc-400" />
                            <span>{video.views}</span>
                          </div>
                        )}
                        {video.likes && video.likes !== 'N/A' && (
                          <div className="flex items-center gap-1">
                            <Heart size={16} className="text-zinc-400" />
                            <span>{video.likes}</span>
                          </div>
                        )}
                        {video.date && video.date !== 'N/A' && (
                          <div className="flex items-center gap-1">
                            <Calendar size={16} className="text-zinc-400" />
                            <span>{video.date}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                
                {hasMoreVideos && (
                  <button 
                    onClick={() => setShowAllVideos(true)}
                    className="mt-4 w-full py-3 border border-zinc-200 rounded-lg text-sm font-medium text-zinc-700 hover:bg-zinc-50 hover:text-emerald-600 hover:border-emerald-200 transition-all flex items-center justify-center gap-2"
                  >
                    <Maximize2 size={16} />
                    Ver todos os {baseData.recentVideos.length} vídeos extraídos
                  </button>
                )}
              </>
            ) : (
              <div className="text-center py-8 text-zinc-500 bg-zinc-50 rounded-lg border border-zinc-100 border-dashed">
                <Video size={32} className="mx-auto mb-3 text-zinc-400" />
                <p>Nenhum vídeo recente encontrado ou a plataforma bloqueou a leitura pública.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal for All Videos */}
      {showAllVideos && baseData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[85vh] flex flex-col animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between p-6 border-b border-zinc-100">
              <div>
                <h2 className="text-xl font-bold text-zinc-900">Todos os Vídeos Extraídos</h2>
                <p className="text-sm text-zinc-500">Mostrando {baseData.recentVideos.length} vídeos de {baseData.username}</p>
              </div>
              <button 
                onClick={() => setShowAllVideos(false)}
                className="p-2 text-zinc-400 hover:text-zinc-600 hover:bg-zinc-100 rounded-full transition-colors"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {baseData.recentVideos.map((video, index) => (
                  <div key={index} className="border border-zinc-200 rounded-lg p-4 hover:border-emerald-300 transition-colors bg-white shadow-sm">
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center text-zinc-500 font-bold text-sm shrink-0">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-zinc-900 mb-3" title={video.title}>
                          {video.title || 'Sem título'}
                        </p>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-600">
                          {video.views && video.views !== 'N/A' && (
                            <div className="flex items-center gap-1 bg-zinc-50 px-2 py-1 rounded">
                              <Eye size={14} className="text-zinc-400" />
                              <span className="font-medium">{video.views}</span>
                            </div>
                          )}
                          {video.likes && video.likes !== 'N/A' && (
                            <div className="flex items-center gap-1 bg-zinc-50 px-2 py-1 rounded">
                              <Heart size={14} className="text-zinc-400" />
                              <span className="font-medium">{video.likes}</span>
                            </div>
                          )}
                          {video.date && video.date !== 'N/A' && (
                            <div className="flex items-center gap-1 bg-zinc-50 px-2 py-1 rounded">
                              <Calendar size={14} className="text-zinc-400" />
                              <span className="font-medium">{video.date}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
