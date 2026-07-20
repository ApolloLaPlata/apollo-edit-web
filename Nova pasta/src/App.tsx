import React, { useState, useEffect } from 'react';
import { Loader2, FileText, CheckCircle2, AlertCircle, Camera, Newspaper, ExternalLink, Search, Download, UploadCloud, X, RefreshCw, Image as ImageIcon, Files, Smile, LineChart, Trash2, Flame, Copy, Palette, PenTool, ImagePlus, BookOpen, Sparkles, Bot, Monitor, Youtube, ThumbsUp, MessageSquare, Share2, Clock, Bookmark, BookmarkCheck, TrendingUp, Settings as SettingsIcon, Activity, Archive, Target, Radar } from 'lucide-react';
import JSZip from 'jszip';
import { saveAs } from 'file-saver';
import { analyzeScriptForAssets, VisualAsset, AutoImage, fetchHotNews, NewsItem, generateScriptFromNews, generateShortsScriptFromNews, generateScriptFromVideo, generateThumbnailIdeas, deepDiveNews, generateAIImage, verifyAndSelectBestImage, analyzeVideoForIdeas, VideoAnalysisData } from './lib/gemini';
import { RadarYouTube } from './components/RadarYouTube';
import { ImageStudio } from './components/ImageStudio';
import { MyChannel } from './components/MyChannel';
import { Settings } from './components/Settings';
import { Dashboard } from './components/Dashboard';
import { LiveMonitor } from './components/LiveMonitor';
import { History } from './components/History';
import { ScriptsTab } from './components/ScriptsTab';
import { StrategyPanel } from './components/StrategyPanel';
import { ToastContainer, toast } from './components/Toast';
import { optimizeSEOWithOpenRouter } from './lib/openrouter';
import { fetchNewsWithGrok } from './lib/grok';
import ReactMarkdown from 'react-markdown';

const convertToJpeg = (dataUrl: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        resolve(dataUrl); // fallback if canvas fails
        return;
      }
      // Fill white background in case of transparent PNG
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      resolve(canvas.toDataURL('image/jpeg', 0.9));
    };
    img.onerror = () => reject(new Error('Image load error'));
    img.src = dataUrl;
  });
};

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

export default function App() {
  const [script, setScript] = useState(() => localStorage.getItem('saved_script') || '');
  const [imageCount, setImageCount] = useState(8);
  const [autoSelect, setAutoSelect] = useState(false);
  const [allowedTypes, setAllowedTypes] = useState({
    photo: true,
    headline: true,
    object: true,
    comic: false,
    graph: true,
    illustration: true,
    ai_generated: false,
    screenshot: true
  });
  const [aiAspectRatio, setAiAspectRatio] = useState<"16:9" | "9:16" | "1:1">("16:9");
  const [assets, setAssets] = useState<VisualAsset[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshingIndex, setRefreshingIndex] = useState<number | null>(null);
  const [hoveredPreview, setHoveredPreview] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  // News Hunter State
  const [activeTab, setActiveTab] = useState<'strategy' | 'images' | 'news' | 'dashboard' | 'miner' | 'radar' | 'studio' | 'channel' | 'analytics' | 'monitor' | 'settings' | 'history' | 'scripts'>('scripts');
  const [newsTopic, setNewsTopic] = useState('');
  const [selectedTone, setSelectedTone] = useState(localStorage.getItem('setting_tone') || 'jornalistico');
  const [playingVideoUrl, setPlayingVideoUrl] = useState<string | null>(null);
  const [newsCount, setNewsCount] = useState(5);
  const [useGrok, setUseGrok] = useState(false);
  const [newsItems, setNewsItems] = useState<NewsItem[]>(() => {
    const saved = localStorage.getItem('saved_news');
    return saved ? JSON.parse(saved) : [];
  });
  const [isFetchingNews, setIsFetchingNews] = useState(false);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [expandedScreenshot, setExpandedScreenshot] = useState<number | null>(null);

  // New Features State
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [isGeneratingShorts, setIsGeneratingShorts] = useState(false);
  const [thumbnailIdeas, setThumbnailIdeas] = useState<string | null>(null);
  const [isGeneratingThumbnails, setIsGeneratingThumbnails] = useState(false);
  const [deepDives, setDeepDives] = useState<Record<number, string>>({});
  const [isDeepDiving, setIsDeepDiving] = useState<Record<number, boolean>>({});
  const [isGeneratingImage, setIsGeneratingImage] = useState<Record<number, boolean>>({});

  // Dashboard State
  const [dashboardNews, setDashboardNews] = useState<NewsItem[]>([]);
  const [isFetchingDashboard, setIsFetchingDashboard] = useState(false);
  const [dashboardCategory, setDashboardCategory] = useState('Geral');

  // Miner State
  const [minerTopic, setMinerTopic] = useState('');
  const [minerResults, setMinerResults] = useState<any[]>([]);
  const [isMining, setIsMining] = useState(false);
  const [videoAnalysis, setVideoAnalysis] = useState<Record<string, VideoAnalysisData>>({});
  const [isAnalyzingVideo, setIsAnalyzingVideo] = useState<Record<string, boolean>>({});
  const [isGeneratingVideoScript, setIsGeneratingVideoScript] = useState<Record<string, boolean>>({});
  const [savedVideos, setSavedVideos] = useState<any[]>(() => {
    const saved = localStorage.getItem('saved_videos');
    return saved ? JSON.parse(saved) : [];
  });

  // OpenRouter State
  const [openRouterApiKey, setOpenRouterApiKey] = useState(() => localStorage.getItem('openrouter_api_key') || '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');
  const [isOptimizingSEO, setIsOptimizingSEO] = useState(false);
  const [seoResult, setSeoResult] = useState('');

  useEffect(() => {
    localStorage.setItem('saved_script', script);
  }, [script]);

  useEffect(() => {
    localStorage.setItem('openrouter_api_key', openRouterApiKey);
  }, [openRouterApiKey]);

  useEffect(() => {
    localStorage.setItem('saved_news', JSON.stringify(newsItems));
  }, [newsItems]);

  useEffect(() => {
    localStorage.setItem('saved_videos', JSON.stringify(savedVideos));
  }, [savedVideos]);

  const handleToggleSaveVideo = (video: any) => {
    setSavedVideos(prev => {
      const isSaved = prev.some(v => v.url === video.url);
      if (isSaved) {
        return prev.filter(v => v.url !== video.url);
      } else {
        return [...prev, video];
      }
    });
  };

  const PREDEFINED_TOPICS = [
    // Política e Economia (Core)
    "Política Nacional", "Economia", "Brasília", "STF e Judiciário", 
    "Congresso Nacional", "Eleições", "Investigações", "Mercado Financeiro",
    
    // Mundo e Tecnologia
    "Política Internacional", "Mundo", "Inteligência Artificial", 
    "Tecnologia", "Clima e Meio Ambiente", "Guerras e Conflitos",
    
    // Viral e Urgente (Broad Importance)
    "Assuntos do Momento", "Viralizou na Internet", "Trends do TikTok", 
    "Polêmicas", "Urgente", "Comportamento",
    
    // Entretenimento e Sociedade
    "Fofoca", "Redes Sociais", "Entretenimento", "Cultura Pop", 
    "Celebridades", "Esportes", "Saúde", "Polícia", "Música e Shows"
  ];

  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const selectAutoImage = async (assetIndex: number, img: AutoImage): Promise<boolean> => {
    try {
      // We need to fetch the image through our proxy to avoid CORS and get it as base64
      let res = await fetch(`/api/proxy-image?url=${encodeURIComponent(img.url)}`);
      
      // If full image fails, try thumbnail as fallback
      if (!res.ok && img.thumbnail) {
        res = await fetch(`/api/proxy-image?url=${encodeURIComponent(img.thumbnail)}`);
      }
      
      if (!res.ok) throw new Error('Failed to fetch image and thumbnail');
      
      const blob = await res.blob();
      return new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const dataUrl = e.target?.result as string;
          setAssets(prev => prev.map((a, i) => 
            i === assetIndex ? { ...a, userImage: dataUrl, selectedSourceUrl: img.source } : a
          ));
          resolve(true);
        };
        reader.onerror = () => {
          toast.error('Erro ao processar a imagem. Tente outra opção.');
          resolve(false);
        };
        reader.readAsDataURL(blob);
      });
    } catch (e) {
      console.error(e);
      toast.error('Erro ao carregar esta imagem (bloqueada pelo servidor de origem). Tente outra.');
      return false;
    }
  };

  const handleRefreshImages = async (index: number, searchQuery: string) => {
    setRefreshingIndex(index);
    try {
      const res = await fetch(`/api/search-images?q=${encodeURIComponent(searchQuery)}`);
      
      if (res.ok) {
        const data = await res.json();
        if (data.urls && data.urls.length > 0) {
          setAssets(prev => prev.map((a, i) => 
            i === index ? { ...a, autoImages: data.urls } : a
          ));
        } else {
          toast.info('Não foram encontradas novas imagens para esta busca.');
        }
      } else {
        throw new Error('Failed to fetch new images');
      }
    } catch (e) {
      console.error("Error refreshing images:", e);
      toast.error('Erro ao buscar novas imagens. Tente novamente.');
    } finally {
      setRefreshingIndex(null);
    }
  };

  const handleAnalyze = async () => {
    if (!script.trim()) {
      setError('Por favor, insira um roteiro de notícias.');
      return;
    }

    const activeTypes = Object.entries(allowedTypes).filter(([_, isAllowed]) => isAllowed).map(([type]) => type);
    if (activeTypes.length === 0) {
      setError('Por favor, selecione pelo menos um tipo de imagem permitido.');
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setAssets([]);
    
    try {
      const extractedAssets = await analyzeScriptForAssets(script, imageCount, activeTypes);
      setAssets(extractedAssets);

      if (autoSelect) {
        // Automatically select the best working image for each asset
        await Promise.all(extractedAssets.map(async (asset, i) => {
          if (asset.type === 'ai_generated') {
            try {
              const base64Img = await generateAIImage(asset.searchQuery, aiAspectRatio);
              setAssets(prev => prev.map((a, idx) => idx === i ? { ...a, userImage: base64Img, selectedSourceUrl: 'Gerado por IA' } : a));
            } catch (e) {
              console.error("AI Image generation failed", e);
            }
            return;
          }

          if (asset.autoImages && asset.autoImages.length > 0) {
            try {
              const topOptions = asset.autoImages.slice(0, 4);
              const base64Images: string[] = [];
              const validOptions: AutoImage[] = [];

              for (const opt of topOptions) {
                try {
                  const proxyRes = await fetch(`/api/proxy-image?url=${encodeURIComponent(opt.url)}`);
                  if (proxyRes.ok) {
                    const blob = await proxyRes.blob();
                    const base64 = await new Promise<string>((resolve) => {
                      const reader = new FileReader();
                      reader.onload = () => resolve(reader.result as string);
                      reader.readAsDataURL(blob);
                    });
                    base64Images.push(base64);
                    validOptions.push(opt);
                  }
                } catch (e) { }
              }

              let bestIndex = 0;
              if (base64Images.length > 1) {
                bestIndex = await verifyAndSelectBestImage(asset.context, base64Images);
              }

              if (validOptions[bestIndex]) {
                setAssets(prev => prev.map((a, idx) => idx === i ? { ...a, userImage: base64Images[bestIndex], selectedSourceUrl: validOptions[bestIndex].source } : a));
              } else if (validOptions.length > 0) {
                setAssets(prev => prev.map((a, idx) => idx === i ? { ...a, userImage: base64Images[0], selectedSourceUrl: validOptions[0].source } : a));
              }
            } catch (e) {
              console.error("Double verification failed", e);
              // fallback to normal auto select
              for (const img of asset.autoImages.slice(0, 3)) {
                const success = await selectAutoImage(i, img);
                if (success) break;
              }
            }
          }
        }));
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || 'Ocorreu um erro ao processar o roteiro.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleImageUpload = (index: number, file: File) => {
    if (!file.type.startsWith('image/')) {
      toast.error('Por favor, selecione um arquivo de imagem válido.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const dataUrl = e.target?.result as string;
      setAssets(prev => prev.map((a, i) => 
        i === index ? { ...a, userImage: dataUrl, selectedSourceUrl: undefined } : a
      ));
    };
    reader.readAsDataURL(file);
  };

  const removeImage = (index: number) => {
    setAssets(prev => prev.map((a, i) => 
      i === index ? { ...a, userImage: undefined, selectedSourceUrl: undefined } : a
    ));
  };

  const handleDownloadZip = async () => {
    const zip = new JSZip();
    const folder = zip.folder('imagens_noticias');
    
    if (!folder) return;

    let count = 0;
    for (let i = 0; i < assets.length; i++) {
      const asset = assets[i];
      if (asset.userImage) {
        try {
          // Convert to JPEG
          const jpegDataUrl = await convertToJpeg(asset.userImage);
          const base64Data = jpegDataUrl.split(',')[1];
          // Name sequentially: imagem 1.jpg, imagem 2.jpg, etc.
          folder.file(`imagem ${i + 1}.jpg`, base64Data, { base64: true });
          count++;
        } catch (e) {
          console.error('Failed to convert image for zip', e);
        }
      }
    }

    if (count === 0) {
      toast.info('Nenhuma imagem selecionada para baixar.');
      return;
    }

    const content = await zip.generateAsync({ type: 'blob' });
    saveAs(content, 'imagens_noticias.zip');
  };

  const handleDownloadLoose = async () => {
    let count = 0;
    for (let i = 0; i < assets.length; i++) {
      const asset = assets[i];
      if (asset.userImage) {
        try {
          // Convert to JPEG
          const jpegDataUrl = await convertToJpeg(asset.userImage);
          saveAs(jpegDataUrl, `imagem ${i + 1}.jpg`);
          count++;
          // Small delay to prevent browser from blocking multiple rapid downloads
          await delay(300);
        } catch (e) {
          console.error('Failed to convert/download image', e);
        }
      }
    }
    
    if (count === 0) {
      toast.info('Nenhuma imagem selecionada para baixar.');
    }
  };

  const handleDownloadSingle = async (asset: VisualAsset, index: number) => {
    if (!asset.userImage) return;
    try {
      const jpegDataUrl = await convertToJpeg(asset.userImage);
      saveAs(jpegDataUrl, `imagem ${index + 1}.jpg`);
    } catch (e) {
      console.error('Failed to convert/download image', e);
      toast.error('Erro ao baixar a imagem.');
    }
  };

  const handleClear = () => {
    if (assets.length > 0 && !window.confirm('Tem certeza que deseja limpar tudo e começar de novo?')) {
      return;
    }
    setScript('');
    setAssets([]);
    setError(null);
  };

  const handleFetchNews = async () => {
    if (!newsTopic.trim()) {
      setNewsError('Por favor, digite um tema para buscar.');
      return;
    }

    setNewsError(null);
    setIsFetchingNews(true);
    setNewsItems([]);
    setExpandedScreenshot(null);

    try {
      let news;
      if (useGrok) {
        const grokKey = localStorage.getItem('api_key_grok');
        if (!grokKey) {
          throw new Error('Chave API do Grok não configurada. Vá em Configurações para adicionar.');
        }
        news = await fetchNewsWithGrok(newsTopic, newsCount, grokKey);
      } else {
        news = await fetchHotNews(newsTopic, newsCount);
      }
      setNewsItems(news);
    } catch (err: any) {
      setNewsError(err.message || 'Erro ao buscar notícias.');
    } finally {
      setIsFetchingNews(false);
    }
  };

  const handleTopicClick = (topic: string) => {
    setNewsTopic(prev => {
      const current = prev.trim();
      if (current) {
        if (current.includes(topic)) return current; // Evita duplicar
        return `${current}, ${topic}`;
      }
      return topic;
    });
  };

  const handleToneChange = (newTone: string) => {
    setSelectedTone(newTone);
    localStorage.setItem('setting_tone', newTone);
  };

  const handleRemoveNewsItem = (indexToRemove: number) => {
    setNewsItems(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const handleCopyNews = () => {
    if (newsItems.length === 0) return;
    
    const textToCopy = newsItems.map((item, index) => {
      return `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
    }).join('\n\n---\n\n');

    navigator.clipboard.writeText(textToCopy).then(() => {
      toast.success('Todas as notícias foram copiadas para a área de transferência!');
    }).catch(err => {
      console.error('Failed to copy text: ', err);
      toast.error('Erro ao copiar o texto.');
    });
  };

  const handleGenerateScript = async () => {
    if (newsItems.length === 0) return;
    setIsGeneratingScript(true);
    try {
      const newScript = await generateScriptFromNews(newsItems);
      setScript(newScript);
      
      // Save to history (limit to 50)
      const savedScripts = JSON.parse(localStorage.getItem('scripts_history') || '[]');
      const newSavedScript = {
        id: Date.now().toString(),
        title: newsItems[0]?.title || 'Roteiro Gerado',
        content: newScript,
        date: new Date().toISOString(),
        type: 'long'
      };
      try {
        localStorage.setItem('scripts_history', JSON.stringify([newSavedScript, ...savedScripts].slice(0, 50)));
      } catch (e) {
        console.warn('Could not save to history, localStorage might be full');
      }
      
      setActiveTab('images');
    } catch (e: any) {
      toast.error(e.message || 'Erro ao gerar roteiro.');
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleGenerateShortsScript = async () => {
    if (newsItems.length === 0) return;
    setIsGeneratingShorts(true);
    try {
      const newScript = await generateShortsScriptFromNews(newsItems);
      setScript(newScript);
      
      // Save to history (limit to 50)
      const savedScripts = JSON.parse(localStorage.getItem('scripts_history') || '[]');
      const newSavedScript = {
        id: Date.now().toString(),
        title: newsItems[0]?.title || 'Roteiro Curto Gerado',
        content: newScript,
        date: new Date().toISOString(),
        type: 'shorts'
      };
      try {
        localStorage.setItem('scripts_history', JSON.stringify([newSavedScript, ...savedScripts].slice(0, 50)));
      } catch (e) {
        console.warn('Could not save to history, localStorage might be full');
      }
      
      setActiveTab('images');
    } catch (e: any) {
      toast.error(e.message || 'Erro ao gerar roteiro para Shorts/TikTok.');
    } finally {
      setIsGeneratingShorts(false);
    }
  };

  const handleGenerateThumbnails = async () => {
    if (!script.trim()) return;
    setIsGeneratingThumbnails(true);
    try {
      const ideas = await generateThumbnailIdeas(script);
      setThumbnailIdeas(ideas);
    } catch (e: any) {
      toast.error(e.message || 'Erro ao gerar ideias de thumbnail.');
    } finally {
      setIsGeneratingThumbnails(false);
    }
  };

  const handleOptimizeSEO = async () => {
    if (!script.trim()) return;
    if (!openRouterApiKey.trim()) {
      toast.error('Por favor, configure sua chave API do OpenRouter.');
      return;
    }
    
    setIsOptimizingSEO(true);
    try {
      const result = await optimizeSEOWithOpenRouter(script, openRouterApiKey);
      setSeoResult(result);
    } catch (e: any) {
      toast.error(e.message || 'Erro ao otimizar SEO.');
    } finally {
      setIsOptimizingSEO(false);
    }
  };

  const handleDeepDive = async (index: number, item: NewsItem) => {
    setIsDeepDiving(prev => ({ ...prev, [index]: true }));
    try {
      const dive = await deepDiveNews(item.url, item.title);
      setDeepDives(prev => ({ ...prev, [index]: dive }));
    } catch (e: any) {
      toast.error(e.message || 'Erro ao aprofundar notícia.');
    } finally {
      setIsDeepDiving(prev => ({ ...prev, [index]: false }));
    }
  };

  const loadDashboardNews = async (category: string) => {
    setDashboardCategory(category);
    setIsFetchingDashboard(true);
    try {
      const news = await fetchHotNews(category === 'Geral' ? 'Principais notícias do dia Brasil e Mundo' : category, 12);
      setDashboardNews(news);
    } catch (e: any) {
      console.error(e);
      toast.error(e.message || "Erro ao carregar notícias do painel.");
    } finally {
      setIsFetchingDashboard(false);
    }
  };

  const handleMineVideos = async (topic: string) => {
    if (!topic.trim()) return;
    setActiveTab('miner');
    setMinerTopic(topic);
    setIsMining(true);
    try {
      const res = await fetch(`/api/search-youtube?q=${encodeURIComponent(topic)}`);
      const data = await res.json();
      setMinerResults(data.videos || []);
    } catch (e) {
      console.error(e);
      toast.error('Erro ao buscar vídeos.');
    } finally {
      setIsMining(false);
    }
  };

  const handleAnalyzeVideo = async (video: any) => {
    setIsAnalyzingVideo(prev => ({ ...prev, [video.url]: true }));
    try {
      const analysis = await analyzeVideoForIdeas(video.title, video.description, video.author);
      setVideoAnalysis(prev => ({ ...prev, [video.url]: analysis }));
    } catch (e: any) {
      toast.error(e.message || 'Erro ao analisar vídeo.');
    } finally {
      setIsAnalyzingVideo(prev => ({ ...prev, [video.url]: false }));
    }
  };

  const handleGenerateVideoScript = async (video: any) => {
    setIsGeneratingVideoScript(prev => ({ ...prev, [video.url]: true }));
    try {
      const newScript = await generateScriptFromVideo(video.title, video.description, video.author);
      setScript(newScript);
      
      // Save to history (limit to 50)
      const savedScripts = JSON.parse(localStorage.getItem('scripts_history') || '[]');
      const newSavedScript = {
        id: Date.now().toString(),
        title: `Inspirado em: ${video.title}`,
        content: newScript,
        date: new Date().toISOString(),
        type: 'long'
      };
      try {
        localStorage.setItem('scripts_history', JSON.stringify([newSavedScript, ...savedScripts].slice(0, 50)));
      } catch (e) {
        console.warn('Could not save to history, localStorage might be full');
      }
      
      setActiveTab('images');
    } catch (e: any) {
      toast.error(e.message || 'Erro ao gerar roteiro inspirado no vídeo.');
    } finally {
      setIsGeneratingVideoScript(prev => ({ ...prev, [video.url]: false }));
    }
  };

  const handleGenerateAIImage = async (index: number, asset: VisualAsset) => {
    setIsGeneratingImage(prev => ({ ...prev, [index]: true }));
    try {
      const prompt = `Crie uma imagem realista e de alta qualidade para ser usada em um vídeo de YouTube. Contexto: ${asset.context}. Descrição visual: ${asset.description}. Estilo: ${asset.type === 'photo' ? 'Fotografia realista, iluminação dramática' : asset.type === 'illustration' ? 'Ilustração digital moderna' : 'Imagem clara e direta'}`;
      const imageUrl = await generateAIImage(prompt, "16:9");
      
      setAssets(prev => prev.map((a, i) => {
        if (i === index) {
          return { ...a, userImage: imageUrl, selectedSourceUrl: 'Gerado por IA (Gemini)' };
        }
        return a;
      }));
    } catch (e: any) {
      toast.error(e.message || 'Erro ao gerar imagem com IA.');
    } finally {
      setIsGeneratingImage(prev => ({ ...prev, [index]: false }));
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard' && dashboardNews.length === 0) {
      loadDashboardNews('Geral');
    }
  }, [activeTab]);

  const completedCount = assets.filter(a => a.userImage).length;
  const progressPercentage = assets.length > 0 ? Math.round((completedCount / assets.length) * 100) : 0;
  const hasImages = completedCount > 0;

  return (
    <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans flex">
      {/* Sidebar Spacer */}
      <div className="w-[68px] shrink-0"></div>

      {/* Sidebar */}
      <aside className="fixed top-0 left-0 h-screen bg-white border-r border-zinc-200 flex flex-col z-50 w-[68px] hover:w-64 transition-all duration-300 overflow-hidden group">
        <div className="p-4 border-b border-zinc-200 flex items-center gap-3 whitespace-nowrap h-[65px] shrink-0">
          <div className="bg-indigo-600 p-2 rounded-lg text-white shrink-0">
            <Newspaper size={20} />
          </div>
          <h1 className="text-xl font-semibold tracking-tight opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden">NewsAsset Finder</h1>
        </div>
        
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto overflow-x-hidden">
          <button
            onClick={() => setActiveTab('strategy')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'strategy' ? 'bg-indigo-50 text-indigo-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Target size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Estratégia do Canal</span>
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'dashboard' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Monitor size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Painel Geral</span>
          </button>
          <button
            onClick={() => setActiveTab('images')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'images' ? 'bg-indigo-50 text-indigo-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <ImageIcon size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Buscador de Imagens</span>
          </button>
          <button
            onClick={() => setActiveTab('news')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'news' ? 'bg-orange-50 text-orange-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Flame size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Caçador de Notícias</span>
          </button>
          <button
            onClick={() => setActiveTab('scripts')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'scripts' ? 'bg-indigo-50 text-indigo-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <PenTool size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Roteiros</span>
          </button>
          <button
            onClick={() => setActiveTab('miner')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'miner' ? 'bg-red-50 text-red-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Youtube size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Mineração Viral</span>
          </button>
          <button
            onClick={() => setActiveTab('radar')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'radar' ? 'bg-red-50 text-red-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <TrendingUp size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Radar YouTube</span>
          </button>
          <button
            onClick={() => setActiveTab('studio')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'studio' ? 'bg-indigo-50 text-indigo-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Palette size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Estúdio de Imagens</span>
          </button>
          <button
            onClick={() => setActiveTab('channel')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'channel' ? 'bg-red-50 text-red-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Youtube size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Meu Canal</span>
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'analytics' ? 'bg-emerald-50 text-emerald-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <LineChart size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Analytics</span>
          </button>
          <button
            onClick={() => setActiveTab('monitor')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'monitor' ? 'bg-emerald-50 text-emerald-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Activity size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Monitor Ao Vivo</span>
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'history' ? 'bg-indigo-50 text-indigo-700' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <Archive size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Histórico</span>
          </button>
          <button
            onClick={() => setActiveTab('settings')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors whitespace-nowrap ${activeTab === 'settings' ? 'bg-zinc-100 text-zinc-900' : 'text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900'}`}
          >
            <SettingsIcon size={18} className="shrink-0" />
            <span className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 w-0 group-hover:w-auto overflow-hidden text-left">Configurações</span>
          </button>
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Top Header for actions */}
        <header className="bg-green-500 border-b border-green-600 sticky top-0 z-10 h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8 shrink-0 shadow-md">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-bold text-white capitalize drop-shadow-md">
              {activeTab === 'strategy' ? 'Estratégia do Canal' :
               activeTab === 'dashboard' ? 'Painel Geral' :
               activeTab === 'images' ? 'Buscador de Imagens' :
               activeTab === 'news' ? 'Caçador de Notícias' :
               activeTab === 'miner' ? 'Mineração Viral' :
               activeTab === 'radar' ? 'Radar YouTube' :
               activeTab === 'studio' ? 'Estúdio de Imagens' :
               activeTab === 'channel' ? 'Meu Canal' :
               activeTab === 'analytics' ? 'Analytics' :
               activeTab === 'monitor' ? 'Monitor Ao Vivo' :
               'Configurações'}
            </h2>
          </div>
          
          <div className="flex items-center gap-4">
            {activeTab === 'images' && assets.length > 0 && (
              <div className="flex items-center gap-3 hidden sm:flex">
                <div className="text-sm font-medium text-zinc-500">
                  Progresso: {completedCount}/{assets.length}
                </div>
                <div className="w-32 h-2 bg-zinc-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-500 transition-all duration-500 ease-out"
                    style={{ width: `${progressPercentage}%` }}
                  />
                </div>
              </div>
            )}
            
            {activeTab === 'images' && hasImages && (
              <div className="flex items-center gap-2">
                <button
                  onClick={handleDownloadLoose}
                  className="flex items-center gap-2 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                  title="Baixar arquivos soltos"
                >
                  <Files size={16} />
                  Baixar Soltas
                </button>
                <button
                  onClick={handleDownloadZip}
                  className="flex items-center gap-2 bg-zinc-900 hover:bg-zinc-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                  <Download size={16} />
                  Baixar ZIP
                </button>
              </div>
            )}
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'strategy' ? (
          <StrategyPanel />
        ) : activeTab === 'channel' ? (
          <MyChannel 
            savedVideos={savedVideos}
            handleToggleSaveVideo={handleToggleSaveVideo}
            videoAnalysis={videoAnalysis}
            isAnalyzingVideo={isAnalyzingVideo}
            handleAnalyzeVideo={handleAnalyzeVideo}
            isGeneratingVideoScript={isGeneratingVideoScript}
            handleGenerateVideoScript={handleGenerateVideoScript}
          />
        ) : activeTab === 'radar' ? (
          <RadarYouTube />
        ) : activeTab === 'studio' ? (
          <ImageStudio />
        ) : activeTab === 'analytics' ? (
          <Dashboard />
        ) : activeTab === 'monitor' ? (
          <LiveMonitor />
        ) : activeTab === 'history' ? (
          <History />
        ) : activeTab === 'scripts' ? (
          <ScriptsTab />
        ) : activeTab === 'settings' ? (
          <Settings />
        ) : activeTab === 'dashboard' ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h2 className="text-2xl font-bold text-zinc-900">Painel Geral</h2>
                <button
                  onClick={() => {
                    if (dashboardNews.length === 0) return;
                    const textToCopy = dashboardNews.map((item) => {
                      return `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
                    }).join('\n\n---\n\n');
                    navigator.clipboard.writeText(textToCopy).then(() => {
                      toast.success('Todas as notícias foram copiadas para a área de transferência!');
                    }).catch(err => {
                      console.error('Failed to copy text: ', err);
                      toast.error('Erro ao copiar o texto.');
                    });
                  }}
                  className="flex items-center gap-2 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                  title="Copiar todas as notícias"
                >
                  <Copy size={16} />
                  Copiar Tudo
                </button>
              </div>
              <div className="flex gap-2 overflow-x-auto pb-2">
                {['Geral', 'Política', 'Economia', 'Mundo', 'Tecnologia', 'Entretenimento'].map(cat => (
                  <button
                    key={cat}
                    onClick={() => loadDashboardNews(cat)}
                    className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${dashboardCategory === cat ? 'bg-zinc-900 text-white' : 'bg-white border border-zinc-200 text-zinc-600 hover:bg-zinc-50'}`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {isFetchingDashboard ? (
              <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
                <Loader2 size={32} className="animate-spin mb-4 text-indigo-600" />
                <p>Buscando os últimos acontecimentos...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {dashboardNews.map((item, index) => (
                  <div key={index} className="bg-white rounded-xl border border-zinc-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
                    {item.imageUrl && (
                      <div className="h-48 overflow-hidden bg-zinc-100 flex-shrink-0">
                        <img 
                          src={`/api/proxy-image?url=${encodeURIComponent(item.imageUrl)}`} 
                          alt={item.title} 
                          className="w-full h-full object-cover" 
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            if (target.src.includes('/api/proxy-image')) {
                              // Fallback to raw URL
                              target.src = item.imageUrl || '';
                            } else {
                              // If raw URL also fails, hide the image container
                              const parent = target.parentElement;
                              if (parent) parent.style.display = 'none';
                            }
                          }}
                        />
                      </div>
                    )}
                    <div className="p-4 flex-1 flex flex-col">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold px-2 py-1 bg-zinc-100 text-zinc-600 rounded-md">
                          {item.source}
                        </span>
                        <span className="text-xs text-zinc-400">{item.date}</span>
                      </div>
                      <h3 className="font-bold text-zinc-900 mb-2 line-clamp-3 leading-snug">{item.title}</h3>
                      <p className="text-sm text-zinc-600 line-clamp-3 mb-4 flex-1">{item.summary}</p>
                      
                      <div className="flex items-center gap-2 mt-auto pt-4 border-t border-zinc-100">
                        <button 
                          onClick={() => {
                            setNewsTopic(item.title);
                            setActiveTab('news');
                          }}
                          className="flex-1 bg-orange-50 hover:bg-orange-100 text-orange-700 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-1"
                          title="Aprofundar no Caçador de Notícias"
                        >
                          <Search size={14} />
                          Aprofundar
                        </button>
                        <button 
                          onClick={() => handleMineVideos(item.title)}
                          className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-1"
                          title="Minerar vídeos no YouTube"
                        >
                          <Youtube size={14} />
                          Minerar
                        </button>
                        <button
                          onClick={() => {
                            const text = `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
                            navigator.clipboard.writeText(text).then(() => toast.success('Notícia copiada!'));
                          }}
                          className="p-2 bg-zinc-50 hover:bg-indigo-50 text-zinc-600 hover:text-indigo-600 rounded-md transition-colors"
                          title="Copiar notícia"
                        >
                          <Copy size={16} />
                        </button>
                        <a 
                          href={item.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="p-2 bg-zinc-50 hover:bg-zinc-100 text-zinc-600 rounded-md transition-colors"
                          title="Ler notícia original"
                        >
                          <ExternalLink size={16} />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : activeTab === 'miner' ? (
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-zinc-200 p-6">
              <h2 className="text-2xl font-bold text-zinc-900 mb-2 flex items-center gap-2">
                <Youtube className="text-red-600" size={28} />
                Mineração Viral no YouTube
              </h2>
              <p className="text-zinc-600 mb-6">
                Busque por vídeos em destaque no YouTube para investigar assuntos, encontrar novos ângulos e gerar ideias de pautas para o seu canal.
              </p>
              
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <input
                    type="text"
                    value={minerTopic}
                    onChange={(e) => {
                      setMinerTopic(e.target.value);
                    }}
                    placeholder="Digite o assunto ou notícia para minerar vídeos..."
                    className="w-full rounded-md bg-white border border-zinc-300 shadow-sm focus:border-red-500 focus:ring-red-500 px-4 py-3 text-lg pr-10"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleMineVideos(minerTopic);
                      }
                    }}
                  />
                  {minerTopic && (
                    <button
                      onClick={() => setMinerTopic('')}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-red-500"
                    >
                      <X size={18} />
                    </button>
                  )}
                </div>
                <button
                  onClick={() => {
                    handleMineVideos(minerTopic);
                  }}
                  disabled={isMining || !minerTopic.trim()}
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
                >
                  {isMining ? <Loader2 size={20} className="animate-spin" /> : <Search size={20} />}
                  Minerar
                </button>
              </div>
            </div>

            {isMining ? (
              <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
                <Loader2 size={40} className="animate-spin mb-4 text-red-600" />
                <p className="text-lg">Varrendo o YouTube em busca de vídeos virais...</p>
              </div>
            ) : minerResults.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {minerResults.map((video, index) => {
                  const isSaved = savedVideos.some(v => v.url === video.url);
                  return (
                  <div key={index} className="bg-white rounded-xl border border-zinc-200 overflow-hidden hover:shadow-md transition-shadow flex flex-col">
                    <div className="relative aspect-video bg-zinc-100">
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
                      <h3 className="font-bold text-zinc-900 mb-1 line-clamp-2 leading-snug" title={video.title}>{video.title}</h3>
                      <div className="flex items-center gap-2 mb-3 text-xs text-zinc-500">
                        <span className="font-medium text-zinc-700">{video.author}</span>
                        <span>•</span>
                        <span>{video.ago}</span>
                      </div>
                      
                      <div className="grid grid-cols-4 gap-2 mb-4 text-xs text-zinc-600 bg-zinc-50 p-2 rounded-lg border border-zinc-100">
                        <div className="flex flex-col items-center justify-center text-center" title="Visualizações">
                          <Monitor size={14} className="mb-1 text-zinc-400" />
                          <span className="font-semibold text-zinc-700">{video.views >= 1000000 ? (video.views/1000000).toFixed(1) + 'M' : video.views >= 1000 ? (video.views/1000).toFixed(1) + 'K' : video.views}</span>
                        </div>
                        <div className="flex flex-col items-center justify-center text-center" title="Curtidas (Estimativa)">
                          <ThumbsUp size={14} className="mb-1 text-zinc-400" />
                          <span className="font-semibold text-zinc-700">{video.likes >= 1000000 ? (video.likes/1000000).toFixed(1) + 'M' : video.likes >= 1000 ? (video.likes/1000).toFixed(1) + 'K' : video.likes}</span>
                        </div>
                        <div className="flex flex-col items-center justify-center text-center" title="Comentários (Estimativa)">
                          <MessageSquare size={14} className="mb-1 text-zinc-400" />
                          <span className="font-semibold text-zinc-700">{video.comments >= 1000000 ? (video.comments/1000000).toFixed(1) + 'M' : video.comments >= 1000 ? (video.comments/1000).toFixed(1) + 'K' : video.comments}</span>
                        </div>
                        <div className="flex flex-col items-center justify-center text-center" title="Compartilhamentos (Estimativa)">
                          <Share2 size={14} className="mb-1 text-zinc-400" />
                          <span className="font-semibold text-zinc-700">{video.shares >= 1000000 ? (video.shares/1000000).toFixed(1) + 'M' : video.shares >= 1000 ? (video.shares/1000).toFixed(1) + 'K' : video.shares}</span>
                        </div>
                      </div>

                      <p className="text-sm text-zinc-600 line-clamp-2 mb-4 flex-1">{video.description}</p>
                      
                      <div className="mt-auto pt-4 border-t border-zinc-100 space-y-3">
                        <div className="flex gap-2">
                          <button 
                            onClick={() => handleAnalyzeVideo(video)}
                            disabled={isAnalyzingVideo[video.url]}
                            className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 py-2 rounded-md text-sm font-medium transition-colors flex items-center justify-center gap-1 disabled:opacity-50"
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
                            className="p-2 bg-zinc-50 hover:bg-zinc-100 text-zinc-600 rounded-md transition-colors"
                            title="Assistir no App"
                          >
                            <ExternalLink size={16} />
                          </button>
                        </div>
                        
                        {videoAnalysis[video.url] && (
                          <div className="bg-red-50/50 rounded-lg p-4 text-sm text-zinc-700 border border-red-100 animate-in fade-in slide-in-from-top-2 space-y-4">
                            <div className="font-bold text-red-900 flex items-center gap-1 border-b border-red-200 pb-2">
                              <Bot size={16} /> Análise de Dados do Vídeo
                            </div>
                            
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Sentimento</span>
                                <span className="bg-white px-2 py-1 rounded border border-zinc-200 inline-block">{videoAnalysis[video.url].sentiment}</span>
                              </div>
                              <div>
                                <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Público-Alvo</span>
                                <span className="bg-white px-2 py-1 rounded border border-zinc-200 inline-block">{videoAnalysis[video.url].targetAudience}</span>
                              </div>
                              <div>
                                <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Apelo Emocional</span>
                                <span className="bg-white px-2 py-1 rounded border border-zinc-200 inline-block">{videoAnalysis[video.url].emotionalAppeal}</span>
                              </div>
                              <div>
                                <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Controvérsia</span>
                                <span className="bg-white px-2 py-1 rounded border border-zinc-200 inline-block">{videoAnalysis[video.url].controversyLevel}</span>
                              </div>
                            </div>

                            <div>
                              <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Ganchos Principais</span>
                              <ul className="list-disc pl-4 space-y-1">
                                {videoAnalysis[video.url].keyHooks.map((hook, i) => <li key={i}>{hook}</li>)}
                              </ul>
                            </div>

                            <div>
                              <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Fatores de Viralização</span>
                              <ul className="list-disc pl-4 space-y-1">
                                {videoAnalysis[video.url].viralFactors.map((factor, i) => <li key={i}>{factor}</li>)}
                              </ul>
                            </div>

                            <div>
                              <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Pontos para Checagem (Fact-Check)</span>
                              <ul className="list-disc pl-4 space-y-1">
                                {videoAnalysis[video.url].factCheckPoints.map((point, i) => <li key={i}>{point}</li>)}
                              </ul>
                            </div>

                            <div className="bg-white p-3 rounded border border-zinc-200">
                              <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">Ideias de Títulos para o seu Canal</span>
                              <ul className="list-disc pl-4 space-y-1 font-medium text-red-700">
                                {videoAnalysis[video.url].suggestedTitles.map((title, i) => <li key={i}>{title}</li>)}
                              </ul>
                            </div>

                            <div>
                              <span className="font-semibold text-zinc-900 block text-xs uppercase tracking-wider mb-1">O que faltou falar (Gaps)</span>
                              <p className="bg-white p-2 rounded border border-zinc-200">{videoAnalysis[video.url].contentGaps}</p>
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
            ) : minerTopic && !isMining ? (
              <div className="bg-white rounded-xl border border-zinc-200 p-12 text-center">
                <Youtube size={48} className="mx-auto text-zinc-300 mb-4" />
                <h3 className="text-lg font-medium text-zinc-900 mb-2">Nenhum vídeo encontrado</h3>
                <p className="text-zinc-500">Tente buscar por termos diferentes ou mais abrangentes.</p>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-20 text-zinc-400 border-2 border-dashed border-zinc-200 rounded-xl bg-zinc-50/50">
                <Youtube size={48} className="mb-4 opacity-50" />
                <p className="text-lg font-medium text-zinc-600">Nenhum vídeo minerado ainda</p>
                <p className="text-sm mt-1">Digite um assunto acima e clique em Minerar.</p>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            
            {/* Left Column: Input */}
            <div className="lg:col-span-4 space-y-6">
              {activeTab === 'images' ? (
              <div className="bg-white rounded-xl shadow-sm border border-zinc-200 p-6 sticky top-24">
                <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                  <FileText size={18} className="text-zinc-500" />
                  Roteiro da Notícia
                </h2>
                <p className="text-sm text-zinc-500 mb-4">
                  Cole o roteiro do seu vídeo. A IA vai ler o texto, dividir os temas e buscar opções de imagens reais para você.
                </p>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Quantidade de Imagens</label>
                  <input 
                    type="number" 
                    min="1" 
                    max="20"
                    value={imageCount}
                    onChange={(e) => setImageCount(parseInt(e.target.value) || 8)}
                    className="w-full p-2 bg-white border border-zinc-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                    disabled={isAnalyzing}
                  />
                </div>

                <div className="mb-4 flex items-center justify-between bg-zinc-50 p-3 rounded-lg border border-zinc-200">
                  <div>
                    <label className="block text-sm font-medium text-zinc-900">Seleção Automática</label>
                    <p className="text-xs text-zinc-500">A IA escolhe a melhor imagem automaticamente.</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="sr-only peer" 
                      checked={autoSelect} 
                      onChange={(e) => setAutoSelect(e.target.checked)} 
                      disabled={isAnalyzing} 
                    />
                    <div className="w-11 h-6 bg-zinc-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-indigo-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                  </label>
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-zinc-700 mb-2">Tipos de Imagem Permitidos</label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: 'photo', label: 'Foto Real', icon: <Camera size={14} /> },
                      { id: 'headline', label: 'Manchete', icon: <Newspaper size={14} /> },
                      { id: 'object', label: 'Objeto/Lugar', icon: <ImageIcon size={14} /> },
                      { id: 'comic', label: 'Cômico/Meme', icon: <Smile size={14} /> },
                      { id: 'graph', label: 'Gráfico/Dado', icon: <LineChart size={14} /> },
                      { id: 'illustration', label: 'Desenho/Ilustração', icon: <Palette size={14} /> },
                      { id: 'ai_generated', label: 'Gerado por IA', icon: <Bot size={14} /> },
                      { id: 'screenshot', label: 'Print/Rede Social', icon: <Monitor size={14} /> },
                    ].map((type) => (
                      <label key={type.id} className={`flex items-center gap-2 p-2 rounded-md border cursor-pointer transition-colors ${allowedTypes[type.id as keyof typeof allowedTypes] ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-zinc-200 text-zinc-500 hover:bg-zinc-50'}`}>
                        <input
                          type="checkbox"
                          className="sr-only"
                          checked={allowedTypes[type.id as keyof typeof allowedTypes]}
                          onChange={(e) => setAllowedTypes(prev => ({ ...prev, [type.id]: e.target.checked }))}
                          disabled={isAnalyzing}
                        />
                        {type.icon}
                        <span className="text-xs font-medium">{type.label}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {allowedTypes.ai_generated && (
                  <div className="mb-4 bg-indigo-50/50 p-3 rounded-lg border border-indigo-100 animate-in fade-in slide-in-from-top-2 duration-200">
                    <label className="block text-sm font-medium text-indigo-900 mb-2">Formato da Imagem IA</label>
                    <div className="flex gap-2">
                      {[
                        { id: '16:9', label: 'Horizontal (YouTube)' },
                        { id: '9:16', label: 'Vertical (Shorts)' },
                        { id: '1:1', label: 'Quadrado (Insta)' }
                      ].map(ratio => (
                        <button
                          key={ratio.id}
                          onClick={() => setAiAspectRatio(ratio.id as any)}
                          className={`flex-1 py-1.5 text-xs font-medium rounded-md border transition-colors ${aiAspectRatio === ratio.id ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-indigo-700 border-indigo-200 hover:bg-indigo-50'}`}
                        >
                          {ratio.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between mb-1">
                  <label className="block text-sm font-medium text-zinc-700">Texto do Roteiro</label>
                  <div className="flex items-center gap-3">
                    {script.trim() && (
                      <button 
                        onClick={() => setScript('')}
                        className="text-xs text-zinc-500 hover:text-red-500 transition-colors"
                      >
                        Limpar
                      </button>
                    )}
                  </div>
                </div>
                <textarea
                  value={script}
                  onChange={(e) => setScript(e.target.value)}
                  placeholder="Ex: Hoje, o mercado financeiro abriu em alta após o anúncio das novas medidas econômicas. O ministro da fazenda discursou pela manhã..."
                  className="w-full h-64 p-3 bg-white border border-zinc-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none text-sm"
                  disabled={isAnalyzing}
                />

                <div className="mt-4 border-t border-zinc-200 pt-4 space-y-3">
                  <button
                    onClick={handleGenerateThumbnails}
                    disabled={isGeneratingThumbnails || !script.trim()}
                    className="w-full flex items-center justify-center gap-2 bg-zinc-100 hover:bg-zinc-200 disabled:bg-zinc-50 text-zinc-700 px-4 py-2.5 rounded-md text-sm font-medium transition-colors border border-zinc-300"
                    title="Gera apenas ideias em texto de como a capa do vídeo deveria ser (não gera a imagem)"
                  >
                    {isGeneratingThumbnails ? <Loader2 size={16} className="animate-spin" /> : <ImagePlus size={16} />}
                    💡 Sugerir Ideias de Thumbnail (Texto)
                  </button>

                  <button
                    onClick={handleOptimizeSEO}
                    disabled={isOptimizingSEO || !script.trim()}
                    className="w-full flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 disabled:bg-zinc-50 text-emerald-700 px-4 py-2.5 rounded-md text-sm font-medium transition-colors border border-emerald-200"
                    title="Usa a API do OpenRouter (Gemma 3) para criar Títulos, Descrição e Tags virais"
                  >
                    {isOptimizingSEO ? <Loader2 size={16} className="animate-spin" /> : <TrendingUp size={16} />}
                    🚀 Otimizar SEO para YouTube (OpenRouter)
                  </button>
                  
                  {thumbnailIdeas && (
                    <div className="mt-4 bg-indigo-50/50 border border-indigo-100 rounded-lg p-4 animate-in fade-in slide-in-from-top-2 duration-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles size={16} className="text-indigo-600" />
                        <span className="text-sm font-semibold text-indigo-900">Ideias de Capa (Thumbnail)</span>
                      </div>
                      <div className="text-sm text-zinc-700 whitespace-pre-wrap leading-relaxed">
                        {thumbnailIdeas}
                      </div>
                    </div>
                  )}

                  {seoResult && (
                    <div className="mt-4 bg-emerald-50/50 border border-emerald-100 rounded-lg p-4 animate-in fade-in slide-in-from-top-2 duration-200">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp size={16} className="text-emerald-600" />
                        <span className="text-sm font-semibold text-emerald-900">Otimização de SEO (Títulos, Descrição, Tags)</span>
                      </div>
                      <div className="text-sm text-zinc-700 leading-relaxed markdown-body">
                        <ReactMarkdown>{seoResult}</ReactMarkdown>
                      </div>
                    </div>
                  )}
                </div>

                {error && (
                  <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm flex items-start gap-2">
                    <AlertCircle size={16} className="mt-0.5 shrink-0" />
                    <p>{error}</p>
                  </div>
                )}

                <div className="mt-6 flex flex-col gap-3">
                  <div className="flex gap-3">
                    <button
                      onClick={handleClear}
                      disabled={isAnalyzing || (!script.trim() && assets.length === 0)}
                      className="flex-1 flex items-center justify-center gap-2 bg-zinc-200 hover:bg-zinc-300 disabled:bg-zinc-100 disabled:text-zinc-400 text-zinc-700 px-4 py-3 rounded-md text-sm font-medium transition-colors"
                    >
                      <Trash2 size={16} />
                      Limpar
                    </button>
                    <button
                      onClick={handleAnalyze}
                      disabled={isAnalyzing || !script.trim()}
                      className="flex-[2] flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-4 py-3 rounded-md text-sm font-medium transition-colors"
                    >
                      {isAnalyzing ? (
                        <>
                          <Loader2 size={16} className="animate-spin" />
                          Buscando...
                        </>
                      ) : (
                        <>
                          <Search size={16} />
                          Extrair e Buscar
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-zinc-200 p-6 sticky top-24">
                <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
                  <Flame size={18} className="text-orange-500" />
                  Caçador de Notícias Quentes
                </h2>
                <p className="text-sm text-zinc-500 mb-4">
                  Digite um tema e a IA vai buscar as notícias mais recentes e relevantes sobre o assunto para você usar no seu roteiro.
                </p>
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-zinc-700 mb-2">Sugestões de Temas</label>
                  <div className="flex flex-wrap gap-2">
                    {PREDEFINED_TOPICS.map(topic => (
                      <button
                        key={topic}
                        onClick={() => handleTopicClick(topic)}
                        disabled={isFetchingNews}
                        className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                          newsTopic.includes(topic)
                            ? 'bg-orange-100 border-orange-300 text-orange-800' 
                            : 'bg-white border-zinc-200 text-zinc-600 hover:bg-zinc-50 disabled:opacity-50'
                        }`}
                      >
                        {topic}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="mb-4">
                  <div className="flex items-center justify-between mb-1">
                    <label className="block text-sm font-medium text-zinc-700">Tema da Busca</label>
                    {newsTopic.trim() && (
                      <button 
                        onClick={() => setNewsTopic('')}
                        className="text-xs text-zinc-500 hover:text-red-500 transition-colors"
                      >
                        Limpar
                      </button>
                    )}
                  </div>
                  <input 
                    type="text" 
                    value={newsTopic}
                    onChange={(e) => setNewsTopic(e.target.value)}
                    placeholder="Ou digite seu próprio tema aqui..."
                    className="w-full p-2 bg-white border border-zinc-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-sm"
                    disabled={isFetchingNews}
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-zinc-700 mb-1">Quantidade de Notícias</label>
                  <input 
                    type="number" 
                    min="1" 
                    max="10"
                    value={newsCount}
                    onChange={(e) => setNewsCount(parseInt(e.target.value) || 5)}
                    className="w-full p-2 bg-white border border-zinc-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-orange-500 text-sm"
                    disabled={isFetchingNews}
                  />
                </div>

                <div className="mb-4 flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="useGrok"
                    checked={useGrok}
                    onChange={(e) => setUseGrok(e.target.checked)}
                    className="w-4 h-4 text-orange-600 border-zinc-300 rounded focus:ring-orange-500"
                    disabled={isFetchingNews}
                  />
                  <label htmlFor="useGrok" className="text-sm font-medium text-zinc-700 flex items-center gap-1">
                    Buscar no X (Twitter) usando Grok
                    <span className="text-xs bg-zinc-100 text-zinc-500 px-1.5 py-0.5 rounded">Requer API Key</span>
                  </label>
                </div>

                {newsError && (
                  <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md text-sm flex items-start gap-2">
                    <AlertCircle size={16} className="mt-0.5 shrink-0" />
                    <p>{newsError}</p>
                  </div>
                )}

                <button
                  onClick={() => handleFetchNews()}
                  disabled={isFetchingNews || !newsTopic.trim()}
                  className="mt-6 w-full flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white px-4 py-3 rounded-md text-sm font-medium transition-colors"
                >
                  {isFetchingNews ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Buscando Notícias...
                    </>
                  ) : (
                    <>
                      <Search size={16} />
                      Buscar Notícias
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Right Column: Output */}
          <div className="lg:col-span-8">
            {activeTab === 'images' ? (
              <>
                {assets.length === 0 && !isAnalyzing ? (
                  <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-zinc-400 border-2 border-dashed border-zinc-200 rounded-xl bg-zinc-50/50">
                    <ImageIcon size={48} className="mb-4 opacity-50" />
                    <p className="text-lg font-medium text-zinc-600">Nenhum material extraído ainda</p>
                    <p className="text-sm mt-1">Insira seu roteiro ao lado e clique em Extrair.</p>
                  </div>
                ) : isAnalyzing ? (
                  <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-indigo-500">
                    <Loader2 size={48} className="animate-spin mb-4" />
                    <p className="text-lg font-medium">Lendo roteiro e buscando imagens na internet...</p>
                    <p className="text-sm text-zinc-500 mt-2">Isso pode levar alguns segundos.</p>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {assets.map((asset, index) => {
                      const isDone = !!asset.userImage;
                      
                      return (
                        <div 
                          key={asset.id} 
                          className={`bg-white rounded-xl shadow-sm border transition-all duration-200 overflow-hidden ${
                            isDone ? 'border-emerald-200' : 'border-zinc-200'
                          }`}
                        >
                          <div className="p-5 border-b border-zinc-100 flex flex-col sm:flex-row gap-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <span className={`text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1.5 ${
                                  asset.type === 'photo' 
                                    ? 'bg-blue-100 text-blue-700' 
                                    : asset.type === 'headline' 
                                      ? 'bg-orange-100 text-orange-700' 
                                      : asset.type === 'comic'
                                        ? 'bg-yellow-100 text-yellow-700'
                                        : asset.type === 'graph'
                                          ? 'bg-emerald-100 text-emerald-700'
                                          : asset.type === 'illustration'
                                            ? 'bg-pink-100 text-pink-700'
                                            : 'bg-purple-100 text-purple-700'
                                }`}>
                                  {asset.type === 'photo' ? <Camera size={12} /> : 
                                   asset.type === 'headline' ? <Newspaper size={12} /> : 
                                   asset.type === 'comic' ? <Smile size={12} /> :
                                   asset.type === 'graph' ? <LineChart size={12} /> :
                                   asset.type === 'illustration' ? <Palette size={12} /> :
                                   <ImageIcon size={12} />}
                                  
                                  {asset.type === 'photo' ? 'FOTO REAL' : 
                                   asset.type === 'headline' ? 'MANCHETE' : 
                                   asset.type === 'comic' ? 'CÔMICO/MEME' :
                                   asset.type === 'graph' ? 'GRÁFICO/DADO' :
                                   asset.type === 'illustration' ? 'ILUSTRAÇÃO' :
                                   'OBJETO/LUGAR'}
                                </span>
                                <span className="text-xs font-medium text-zinc-400 uppercase tracking-wider">
                                  Imagem {index + 1} de {assets.length}
                                </span>
                                {isDone && (
                                  <span className="ml-auto flex items-center gap-1 text-emerald-600 text-xs font-medium">
                                    <CheckCircle2 size={14} /> Selecionada
                                  </span>
                                )}
                              </div>
                              
                              <h3 className={`text-lg font-medium mb-1 ${isDone ? 'text-zinc-500' : 'text-zinc-900'}`}>
                                {asset.description}
                              </h3>
                              
                              <p className="text-sm text-zinc-500 italic mb-4 border-l-2 border-zinc-200 pl-3">
                                "{asset.context}"
                              </p>
                            </div>
                            
                            {/* Selected Image Preview */}
                            {isDone && (
                              <div className="w-full sm:w-48 flex flex-col gap-2 flex-shrink-0">
                                <div className="aspect-video sm:aspect-square bg-zinc-100 relative rounded-lg overflow-hidden border border-zinc-200">
                                  <img 
                                    src={asset.userImage} 
                                    alt={asset.description}
                                    className="w-full h-full object-cover"
                                  />
                                  <div className="absolute top-2 right-2 flex flex-col gap-2">
                                    <button 
                                      onClick={() => removeImage(index)}
                                      className="bg-black/50 hover:bg-black/70 text-white p-1.5 rounded-full backdrop-blur-sm transition-colors shadow-sm"
                                      title="Remover imagem"
                                    >
                                      <X size={16} />
                                    </button>
                                    <button 
                                      onClick={() => handleDownloadSingle(asset, index)}
                                      className="bg-indigo-600/90 hover:bg-indigo-600 text-white p-1.5 rounded-full backdrop-blur-sm transition-colors shadow-sm"
                                      title="Baixar esta imagem"
                                    >
                                      <Download size={16} />
                                    </button>
                                  </div>
                                </div>
                                {asset.selectedSourceUrl && (
                                  <a 
                                    href={asset.selectedSourceUrl} 
                                    target="_blank" 
                                    rel="noopener noreferrer" 
                                    className="text-[11px] text-indigo-600 hover:text-indigo-800 flex items-center gap-1 font-medium truncate"
                                    title={asset.selectedSourceUrl}
                                  >
                                    <ExternalLink size={10} className="flex-shrink-0" /> 
                                    <span className="truncate">Ver fonte original</span>
                                  </a>
                                )}
                              </div>
                            )}
                          </div>

                          {/* Image Selection Area */}
                          {!isDone && (
                            <div className="p-5 bg-zinc-50">
                              <div className="flex items-center justify-between mb-3">
                                <p className="text-sm font-medium text-zinc-700">Opções encontradas na internet:</p>
                                <button
                                  onClick={() => handleRefreshImages(index, asset.searchQuery)}
                                  disabled={refreshingIndex === index}
                                  className="flex items-center gap-1.5 text-xs font-medium text-indigo-600 hover:text-indigo-800 disabled:text-zinc-400 transition-colors"
                                >
                                  <RefreshCw size={14} className={refreshingIndex === index ? "animate-spin" : ""} />
                                  {refreshingIndex === index ? "Buscando..." : "Atualizar Opções"}
                                </button>
                              </div>
                              
                              {asset.autoImages && asset.autoImages.length > 0 ? (
                                <div className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-3 mb-4">
                                  {asset.autoImages.slice(0, 30).map((img, imgIdx) => (
                                    <div
                                      key={imgIdx}
                                      className="aspect-video bg-zinc-200 rounded-md overflow-hidden border-2 border-transparent hover:border-indigo-500 transition-all group relative"
                                      onMouseEnter={() => setHoveredPreview(img.url)}
                                      onMouseLeave={() => setHoveredPreview(null)}
                                    >
                                      <img 
                                        src={`/api/proxy-image?url=${encodeURIComponent(img.thumbnail || img.url)}`} 
                                        alt="Opção" 
                                        className="w-full h-full object-cover"
                                        onError={(e) => {
                                          const target = e.target as HTMLImageElement;
                                          if (target.src.includes('/api/proxy-image')) {
                                            target.src = img.thumbnail || img.url;
                                          } else {
                                            const parent = target.parentElement;
                                            if (parent) parent.style.display = 'none';
                                          }
                                        }}
                                      />
                                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 flex flex-col items-center justify-center gap-2 transition-colors">
                                        <button 
                                          onClick={() => selectAutoImage(index, img)}
                                          className="bg-white text-zinc-900 text-xs font-bold px-3 py-1.5 rounded opacity-0 group-hover:opacity-100 transition-opacity shadow-sm hover:bg-zinc-100"
                                        >
                                          Usar esta
                                        </button>
                                        {img.source && (
                                          <a 
                                            href={img.source} 
                                            target="_blank" 
                                            rel="noopener noreferrer" 
                                            className="bg-zinc-900/80 hover:bg-zinc-900 text-white text-[10px] font-medium px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity shadow-sm flex items-center gap-1 backdrop-blur-sm"
                                            onClick={(e) => e.stopPropagation()}
                                          >
                                            <ExternalLink size={10} /> Fonte
                                          </a>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className="text-sm text-zinc-500 italic mb-4">Nenhuma imagem automática encontrada.</div>
                              )}

                              <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-zinc-200">
                                <span className="text-sm text-zinc-500">Não gostou das opções?</span>
                                
                                <a
                                  href={`https://www.google.com/search?tbm=isch&q=${encodeURIComponent(asset.searchQuery)}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1.5 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                                >
                                  <Search size={14} />
                                  Buscar no Google
                                </a>

                                <label className="inline-flex items-center gap-1.5 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors cursor-pointer">
                                  <UploadCloud size={14} />
                                  Fazer Upload
                                  <input 
                                    type="file" 
                                    accept="image/*" 
                                    className="hidden" 
                                    onChange={(e) => {
                                      if (e.target.files?.[0]) {
                                        handleImageUpload(index, e.target.files[0]);
                                      }
                                    }}
                                  />
                                </label>

                                <button
                                  onClick={() => handleGenerateAIImage(index, asset)}
                                  disabled={isGeneratingImage[index]}
                                  className="inline-flex items-center gap-1.5 bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 text-indigo-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors disabled:opacity-50"
                                  title="Gera uma imagem do zero baseada no contexto (não gera thumbnails)"
                                >
                                  {isGeneratingImage[index] ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
                                  Criar Imagem com IA
                                </button>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            ) : (
              <>
                {newsItems.length === 0 && !isFetchingNews ? (
                  <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-zinc-400 border-2 border-dashed border-zinc-200 rounded-xl bg-zinc-50/50">
                    <Newspaper size={48} className="mb-4 opacity-50" />
                    <p className="text-lg font-medium text-zinc-600">Nenhuma notícia buscada ainda</p>
                    <p className="text-sm mt-1">Digite um tema ao lado e clique em Buscar Notícias.</p>
                  </div>
                ) : isFetchingNews ? (
                  <div className="h-full min-h-[400px] flex flex-col items-center justify-center text-orange-500">
                    <Loader2 size={48} className="animate-spin mb-4" />
                    <p className="text-lg font-medium">Vasculhando a internet por notícias quentes...</p>
                    <p className="text-sm text-zinc-500 mt-2">Isso pode levar alguns segundos.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-4 gap-4">
                      <h2 className="text-xl font-semibold text-zinc-800">Resultados para "{newsTopic}"</h2>
                      <div className="flex flex-wrap items-center gap-2">
                        <select
                          value={selectedTone}
                          onChange={(e) => handleToneChange(e.target.value)}
                          className="px-3 py-1.5 bg-white border border-zinc-300 rounded-md text-sm font-medium text-zinc-700 focus:ring-2 focus:ring-indigo-500 outline-none"
                          title="Tom do Roteiro"
                        >
                          <option value="jornalistico">Jornalístico</option>
                          <option value="viral">Viral / Blog</option>
                          <option value="seo">Foco em SEO</option>
                          <option value="resumo">Resumo Rápido</option>
                        </select>
                        <button 
                          onClick={handleGenerateScript}
                          disabled={isGeneratingScript || isGeneratingShorts}
                          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                        >
                          {isGeneratingScript ? <Loader2 size={16} className="animate-spin" /> : <PenTool size={16} />}
                          Roteiro YouTube
                        </button>
                        <button 
                          onClick={handleGenerateShortsScript}
                          disabled={isGeneratingScript || isGeneratingShorts}
                          className="flex items-center gap-2 bg-black hover:bg-zinc-800 disabled:bg-zinc-500 text-white px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                        >
                          {isGeneratingShorts ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
                          Roteiro TikTok/Shorts
                        </button>
                        <button 
                          onClick={handleCopyNews}
                          className="flex items-center gap-2 bg-white border border-zinc-300 hover:bg-zinc-50 text-zinc-700 px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                        >
                          <Copy size={16} />
                          Copiar Tudo
                        </button>
                      </div>
                    </div>
                    {newsItems.map((item, index) => (
                      <div key={index} className="bg-white rounded-xl shadow-sm border border-zinc-200 p-5 hover:border-orange-200 transition-colors flex flex-col sm:flex-row gap-4">
                        {item.imageUrl && (
                          <div className="w-full sm:w-32 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-zinc-100 border border-zinc-200">
                            <img 
                              src={`/api/proxy-image?url=${encodeURIComponent(item.imageUrl)}`} 
                              alt={item.title}
                              className="w-full h-full object-cover"
                              onError={(e) => {
                                const target = e.target as HTMLImageElement;
                                if (target.src.includes('/api/proxy-image')) {
                                  target.src = item.imageUrl || '';
                                } else {
                                  target.style.display = 'none';
                                }
                              }}
                            />
                          </div>
                        )}
                        <div className="flex-1">
                          <div className="flex items-start justify-between gap-4 mb-2">
                            <h3 className="text-lg font-medium text-zinc-900 leading-tight">
                              {item.title}
                            </h3>
                            <div className="flex items-center gap-2 flex-shrink-0">
                              <span className="bg-orange-100 text-orange-800 text-xs font-bold px-2.5 py-1 rounded-full whitespace-nowrap">
                                {item.source}
                              </span>
                              <button
                                onClick={() => {
                                  const text = `Título: ${item.title}\nResumo: ${item.summary}\nFonte: ${item.source}\nLink: ${item.url}`;
                                  navigator.clipboard.writeText(text).then(() => toast.success('Notícia copiada!'));
                                }}
                                className="text-zinc-400 hover:text-indigo-600 hover:bg-indigo-50 p-1.5 rounded-md transition-colors"
                                title="Copiar notícia"
                              >
                                <Copy size={16} />
                              </button>
                              <button
                                onClick={() => handleRemoveNewsItem(index)}
                                className="text-zinc-400 hover:text-red-600 hover:bg-red-50 p-1.5 rounded-md transition-colors"
                                title="Remover notícia"
                              >
                                <Trash2 size={16} />
                              </button>
                            </div>
                          </div>
                          <p className="text-sm text-zinc-600 mb-3">
                            {item.summary}
                          </p>
                          <div className="flex items-center justify-between mt-auto pt-3 border-t border-zinc-100">
                            <div className="flex items-center gap-4">
                              <span className="text-xs font-medium text-zinc-400">
                                {item.date}
                              </span>
                              <button
                                onClick={() => setExpandedScreenshot(expandedScreenshot === index ? null : index)}
                                className="text-xs font-medium text-zinc-500 hover:text-zinc-800 flex items-center gap-1 transition-colors"
                              >
                                <Camera size={14} />
                                {expandedScreenshot === index ? 'Ocultar Print' : 'Ver Print da Tela'}
                              </button>
                              <button
                                onClick={() => handleDeepDive(index, item)}
                                disabled={isDeepDiving[index]}
                                className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1 transition-colors disabled:opacity-50"
                              >
                                {isDeepDiving[index] ? <Loader2 size={14} className="animate-spin" /> : <BookOpen size={14} />}
                                Resumo Profundo
                              </button>
                              <button
                                onClick={() => handleMineVideos(item.title)}
                                className="text-xs font-medium text-red-600 hover:text-red-800 flex items-center gap-1 transition-colors"
                              >
                                <Youtube size={14} />
                                Minerar no YouTube
                              </button>
                            </div>
                            <a 
                              href={item.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-sm font-medium text-orange-600 hover:text-orange-800 flex items-center gap-1"
                            >
                              Ler matéria completa <ExternalLink size={14} />
                            </a>
                          </div>
                          
                          {/* Deep Dive Section */}
                          {deepDives[index] && (
                            <div className="mt-4 pt-4 border-t border-zinc-100 animate-in fade-in slide-in-from-top-2 duration-200">
                              <div className="flex items-center gap-2 mb-2">
                                <Sparkles size={16} className="text-indigo-600" />
                                <span className="text-sm font-semibold text-indigo-900">Resumo Profundo (Deep Dive)</span>
                              </div>
                              <div className="bg-indigo-50/50 rounded-lg p-4 text-sm text-zinc-700 whitespace-pre-wrap leading-relaxed">
                                {deepDives[index]}
                              </div>
                            </div>
                          )}
                          
                          {/* Screenshot Section */}
                          {expandedScreenshot === index && (
                            <div className="mt-4 pt-4 border-t border-zinc-100 animate-in fade-in slide-in-from-top-2 duration-200">
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-medium text-zinc-500">Print automático da página:</span>
                                <a 
                                  href={`https://image.thum.io/get/width/1200/crop/800/noanimate/${item.url}`}
                                  download={`print-${item.source}.jpg`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-xs flex items-center gap-1 text-indigo-600 hover:text-indigo-800 font-medium"
                                >
                                  <Download size={12} /> Baixar Print
                                </a>
                              </div>
                              <div className="rounded-lg overflow-hidden border border-zinc-200 bg-zinc-50 relative min-h-[200px]">
                                <img 
                                  src={`https://image.thum.io/get/width/1024/crop/800/noanimate/${item.url}`}
                                  alt={`Print da tela de ${item.source}`}
                                  className="w-full h-auto object-cover"
                                  loading="lazy"
                                />
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
      </main>

      {/* Hover Preview Portal */}
      {hoveredPreview && (
        <div 
          className="hidden sm:block fixed z-[100] pointer-events-none bg-white p-2 rounded-xl shadow-2xl border border-zinc-200 transition-all duration-200 ease-out"
          style={{
            top: '50%',
            transform: 'translateY(-50%)',
            left: mousePos.x > window.innerWidth / 2 ? '32px' : 'auto',
            right: mousePos.x > window.innerWidth / 2 ? 'auto' : '32px',
          }}
        >
          <div className="absolute -top-3 left-4 bg-indigo-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-full shadow-sm tracking-wider">
            PREVIEW
          </div>
          <img 
            src={`/api/proxy-image?url=${encodeURIComponent(hoveredPreview)}`} 
            alt="Preview" 
            className="w-auto h-auto max-w-[500px] max-h-[500px] min-w-[250px] min-h-[250px] object-contain rounded-lg bg-zinc-50/80"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              if (target.src.includes('/api/proxy-image')) {
                target.src = hoveredPreview;
              } else {
                target.style.display = 'none';
              }
            }}
          />
        </div>
      )}
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
