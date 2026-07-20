import React, { useState } from 'react';
import { ApiKey, GenerationSettings, StylePreset, KnowledgeDocument } from '../types';
import { MODELS, OPENROUTER_TEXT_MODELS, PROJECT_COLORS, PROJECT_ICONS } from '../constants';
import toast from 'react-hot-toast';
import { Trash2, Plus, Key, AlertCircle, ShieldCheck, Power, RefreshCw, Globe, Palette, Layers, Save, Upload, Loader2, Check, X, Bookmark, Edit2, Layout, Video, Gamepad2, BookOpen, Music, Camera, MonitorPlay, Smartphone, Newspaper, Sword, Ghost, Image as ImageIcon, FileText, Brain, Eye } from 'lucide-react';
import { GoogleGenAI } from "@google/genai";

import { fetchOpenRouterModels } from '../services/openRouterService';
import { checkComfyConnection } from '../services/comfyService';
import { scrapeUrlWithApify } from '../services/apifyService';
import { Project } from '../types';

export const getIconComponent = (iconName: string | undefined, className: string = "w-4 h-4") => {
    switch (iconName) {
        case 'Video': return <Video className={className} />;
        case 'Gamepad2': return <Gamepad2 className={className} />;
        case 'BookOpen': return <BookOpen className={className} />;
        case 'Music': return <Music className={className} />;
        case 'Camera': return <Camera className={className} />;
        case 'Palette': return <Palette className={className} />;
        case 'MonitorPlay': return <MonitorPlay className={className} />;
        case 'Smartphone': return <Smartphone className={className} />;
        case 'Newspaper': return <Newspaper className={className} />;
        case 'Sword': return <Sword className={className} />;
        case 'Ghost': return <Ghost className={className} />;
        case 'Layout':
        default: return <Layout className={className} />;
    }
};

interface SettingsPanelProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  settings: GenerationSettings;
  setSettings: React.Dispatch<React.SetStateAction<GenerationSettings>>;
  onUpdateSetting: (field: keyof GenerationSettings, value: any) => void;
  projects: Project[];
  setProjects: React.Dispatch<React.SetStateAction<Project[]>>;
  activeProjectId: string;
  setActiveProjectId: React.Dispatch<React.SetStateAction<string>>;
}

const resizeImage = (file: File, maxWidth: number, maxHeight: number): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;

                if (width > height) {
                    if (width > maxWidth) {
                        height *= maxWidth / width;
                        width = maxWidth;
                    }
                } else {
                    if (height > maxHeight) {
                        width *= maxHeight / height;
                        height = maxHeight;
                    }
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.drawImage(img, 0, 0, width, height);
                    resolve(canvas.toDataURL('image/jpeg', 0.8));
                } else {
                    resolve(event.target?.result as string);
                }
            };
            img.onerror = reject;
            img.src = event.target?.result as string;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};

const SettingsPanel: React.FC<SettingsPanelProps> = ({
  apiKeys,
  setApiKeys,
  settings,
  setSettings,
  onUpdateSetting,
  projects,
  setProjects,
  activeProjectId,
  setActiveProjectId,
}) => {
  const [newKey, setNewKey] = useState('');
  const [newKeyLabel, setNewKeyLabel] = useState('');
  const [newKeyLimit, setNewKeyLimit] = useState(100);
  const [testingKey, setTestingKey] = useState<string | null>(null);
  const [keyTestResults, setKeyTestResults] = useState<Record<string, 'success' | 'failure' | null>>({});
  
  const [availableTextModels, setAvailableTextModels] = useState(OPENROUTER_TEXT_MODELS);
  const [isSyncingModels, setIsSyncingModels] = useState(false);
  const [isTestingComfy, setIsTestingComfy] = useState(false);
  const [viewingDocument, setViewingDocument] = useState<KnowledgeDocument | null>(null);

  const [scrapingUrl, setScrapingUrl] = useState('');
  const [isScraping, setIsScraping] = useState(false);
  const [isSummarizing, setIsSummarizing] = useState(false);

  const activeProject = projects.find(p => p.id === activeProjectId) || projects[0];

  const handleSummarizeDocument = async () => {
    if (!viewingDocument) return;

    // Use built in gemini or the users gemini key
    const geminiKey = apiKeys.find(k => k.isActive && !k.isRateLimited)?.key || process.env.VITE_GEMINI_API_KEY;
    if (!geminiKey) {
        toast.error("Nenhuma chave Gemini ativa disponível para realizar o resumo.");
        return;
    }

    setIsSummarizing(true);
    const toastId = toast.loading("Analizando e resumindo com IA...");
    
    try {
        const ai = new GoogleGenAI({ apiKey: geminiKey });
        const response = await ai.models.generateContent({
            model: 'gemini-2.5-flash',
            contents: `Você é um curador especialista de banco de dados RAG.
            O usuário anexou um documento gigante que estourou o limite de tokens da API final dele.
            Sua missão é LER o documento abaixo e EXTRAIR apenas o "Puro Suco" para a formatação de roteiros e comandos.
            
            REGRAS PARA O SEU RESUMO:
            1. Descarte absolutamente tudo que for irrelevante: bate-papo de chat, logs de conversa, códigos HTML, menus, propagandas, etc.
            2. Foque EXCLUSIVAMENTE em: Tom de Voz, Regras de Formatação de Roteiro, Personagens, Exemplos Perfeitos de Prompt ou Estrutura Narrativa.
            3. Reescreva o resumo de forma BEM DIRETA, em bullet points, usando MÁXIMO DE ABREVIAÇÕES possíveis para gerar um texto CURTO e ALTAMENTE INFORMATIVO, para economizar Tokens.
            
            TEXTO ORIGINAL DO USUÁRIO:
            ${viewingDocument.content}`,
            config: {
                temperature: 0.2
            }
        });

        const summary = response.text;
        if (!summary) throw new Error("A IA retornou vazio.");

        setViewingDocument(prev => prev ? { ...prev, content: summary } : null);
        toast.success("Resumo extraído com sucesso! Lembre-se de clicar em 'Salvar Alterações'.", { id: toastId });
    } catch (err: any) {
        console.error("Resumo Error:", err);
        toast.error(err.message || "Falha ao gerar resumo.", { id: toastId });
    } finally {
        setIsSummarizing(false);
    }
  };

  const [newPresetName, setNewPresetName] = useState('');

  const handleSavePreset = () => {
    if (!newPresetName.trim()) {
      toast.error("Digite um nome para o preset.");
      return;
    }
    const newPreset = {
      id: crypto.randomUUID(),
      name: newPresetName.trim(),
      globalContext: settings.globalContext || '',
      sceneContext: settings.sceneContext || '',
      negativePrompt: settings.negativePrompt || '',
      styleReferenceImage: settings.styleReferenceImage
    };
    
    setProjects(prev => prev.map(p => p.id === activeProjectId ? {
      ...p,
      presets: [...(p.presets || []), newPreset],
      activePresetId: newPreset.id
    } : p));
    
    setNewPresetName('');
    toast.success("Preset salvo com sucesso no canal atual!");
  };

  const handleLoadPreset = (preset: StylePreset) => {
    setProjects(prev => prev.map(p => p.id === activeProjectId ? {
      ...p,
      activePresetId: preset.id
    } : p));
    toast.success(`Preset "${preset.name}" ativado para este canal!`);
  };

  const handleDeletePreset = (id: string) => {
      setProjects(prev => prev.map(p => p.id === activeProjectId ? {
        ...p,
        presets: p.presets?.filter(preset => preset.id !== id),
        activePresetId: p.activePresetId === id ? undefined : p.activePresetId
      } : p));
      toast.success("Preset removido do canal.");
  };

  const handleSyncModels = async () => {
      if (!settings.openRouterKey) {
          toast.error("Adicione uma chave OpenRouter primeiro.");
          return;
      }
      setIsSyncingModels(true);
      const result = await fetchOpenRouterModels(settings.openRouterKey);
      if (result) {
          // Merge with defaults to ensure we don't lose curated ones if API fails or filters weirdly
          // Actually, let's prioritize the API result but keep defaults if empty
          if (result.textModels.length > 0) setAvailableTextModels(result.textModels);
          toast.success(`Sincronizado! Encontrados ${result.textModels.length} modelos de texto.`);
      } else {
          toast.error("Falha ao sincronizar. Verifique sua chave.");
      }
      setIsSyncingModels(false);
  };

  const handleTestComfyUI = async () => {
      if (!settings.comfyUrl) {
          toast.error("Insira a URL do ComfyUI primeiro.");
          return;
      }
      setIsTestingComfy(true);
      try {
          const isConnected = await checkComfyConnection(settings.comfyUrl, settings.comfyApiKey);
          if (isConnected) {
              toast.success("Conexão com ComfyUI estabelecida com sucesso!");
          }
      } catch (error: any) {
          console.error("ComfyUI Connection Error:", error);
          toast.error(`Falha ao conectar: ${error.message || "Verifique a URL e a API Key."}`);
      } finally {
          setIsTestingComfy(false);
      }
  };

  const addKey = () => {
    if (!newKey.trim()) return;

    // Check for duplicates
    const keyExists = apiKeys.some(k => k.key === newKey.trim());
    if (keyExists) {
        toast.error("Esta chave API já foi adicionada!");
        return;
    }

    setApiKeys((prev) => [
      ...prev,
      { 
          key: newKey.trim(), 
          label: newKeyLabel.trim() || `Chave ${prev.length + 1}`, 
          isActive: true, 
          errorCount: 0,
          usageCount: 0,
          usageLimit: newKeyLimit || 100,
          lastReset: Date.now(),
          isRateLimited: false
      },
    ]);
    setNewKey('');
    setNewKeyLabel('');
    setNewKeyLimit(100);
  };

  const removeKey = (keyToRemove: string) => {
    setApiKeys((prev) => prev.filter((k) => k.key !== keyToRemove));
  };

  const toggleActive = (keyToToggle: string) => {
    setApiKeys((prev) => prev.map(k => 
        k.key === keyToToggle ? { ...k, isActive: !k.isActive } : k
    ));
  };

  const resetUsage = (keyToReset: string) => {
    setApiKeys((prev) => prev.map(k => 
        k.key === keyToReset ? { ...k, usageCount: 0, lastReset: Date.now(), isRateLimited: false } : k
    ));
  };

  const handleScrapeUrl = async () => {
    if (!scrapingUrl.trim()) return;
    if (!settings.apifyApiKey) {
        toast.error("Configure sua chave da API do Apify na seção de 'Serviços Externos' antes de usar este recurso.");
        return;
    }

    setIsScraping(true);
    const toastId = toast.loading("Extraindo conteúdo usando Apify (pode demorar um pouco)...");

    try {
        const content = await scrapeUrlWithApify(scrapingUrl.trim(), settings.apifyApiKey);
        
        // Clean URL for name
        let name = "Web Scraping: " + scrapingUrl.trim().replace(/^https?:\/\//, '').split('/')[0];
        
        const newDoc: KnowledgeDocument = {
            id: crypto.randomUUID(),
            name: name,
            content: `Fonte: ${scrapingUrl.trim()}\n\n${content}`
        };

        handleChange('knowledgeBase', [...(settings.knowledgeBase || []), newDoc]);
        toast.success("Conteúdo extraído e adicionado à base de conhecimento com sucesso!", { id: toastId });
        setScrapingUrl('');
    } catch (error: any) {
        console.error("Apify Error:", error);
        toast.error(error.message || "Erro ao extrair o conteúdo via Apify.", { id: toastId });
    } finally {
        setIsScraping(false);
    }
  };

  const testKey = async (apiKey: string) => {
      if (testingKey) return; // Prevent multiple clicks
      setTestingKey(apiKey);
      setKeyTestResults(prev => ({ ...prev, [apiKey]: null })); // Reset previous result

      let timeoutId: NodeJS.Timeout;

      try {
          // Create a timeout promise (30 seconds)
          const timeoutPromise = new Promise<never>((_, reject) => {
              timeoutId = setTimeout(() => reject(new Error("Timeout: O Google não respondeu em 30s. Verifique sua conexão ou se a chave é válida.")), 30000);
          });

          const ai = new GoogleGenAI({ apiKey });
          // Use a very lightweight API call for speed
          // Race between API and Timeout
          await Promise.race([
            ai.models.get({
                model: 'gemini-2.5-flash'
            }),
            timeoutPromise
          ]);

          setKeyTestResults(prev => ({ ...prev, [apiKey]: 'success' }));
          
          // Auto-heal: If test passes, reset error flags for this key
          setApiKeys(prev => prev.map(k => 
              k.key === apiKey 
                  ? { ...k, errorCount: 0, isRateLimited: false, rateLimitedUntil: 0 } 
                  : k
          ));
          
      } catch (e: any) {
          console.error("Test Key Error:", e);
          setKeyTestResults(prev => ({ ...prev, [apiKey]: 'failure' }));
          toast.error(`❌ FALHA: ${e.message || e.toString()}`); // Keep alert for error details
      } finally {
          if (timeoutId!) clearTimeout(timeoutId);
          setTestingKey(null);
      }
  };

  const handleChange = (field: keyof GenerationSettings, value: any) => {
    onUpdateSetting(field, value);
  };

  const [newProjectName, setNewProjectName] = useState('');
  const [editingProjectId, setEditingProjectId] = useState<string | null>(null);
  const [editingProjectName, setEditingProjectName] = useState('');
  const [editingWorkflow, setEditingWorkflow] = useState<any>(null);
  const [workflowSearchQuery, setWorkflowSearchQuery] = useState('');

  const handleAddProject = () => {
      if (!newProjectName.trim()) return;
      const newProject: Project = {
          id: crypto.randomUUID(),
          name: newProjectName.trim(),
          globalContext: '',
          sceneContext: '',
          negativePrompt: '',
          brandKit: { colors: [] },
          knowledgeBase: []
      };
      setProjects(prev => [...prev, newProject]);
      setNewProjectName('');
  };

  const handleDeleteProject = (id: string) => {
      if (id === 'default') return;
      setProjects(prev => prev.filter(p => p.id !== id));
      if (activeProjectId === id) {
          setActiveProjectId('default');
      }
  };

  const startEditingProject = (project: Project) => {
      setEditingProjectId(project.id);
      setEditingProjectName(project.name);
  };

  const saveRenamedProject = () => {
      if (!editingProjectName.trim() || !editingProjectId) {
          setEditingProjectId(null);
          return;
      }
      setProjects(prev => prev.map(p => 
          p.id === editingProjectId ? { ...p, name: editingProjectName.trim() } : p
      ));
      setEditingProjectId(null);
  };

  const cancelEditingProject = () => {
      setEditingProjectId(null);
      setEditingProjectName('');
  };

  return (
    <div className="space-y-8 p-6 bg-slate-900 rounded-xl border border-slate-700 h-full overflow-y-auto">
      
      {/* --- PROJECTS MANAGEMENT --- */}
      <section className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-400" />
            Gerenciamento de Projetos / Canais
        </h2>
        <p className="text-slate-400 text-sm mb-6">
            Crie projetos separados para organizar personagens e galerias de diferentes canais.
        </p>
        
        <div className="flex flex-col gap-4">
            <div className="flex gap-2">
                <input 
                    type="text" 
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="Nome do novo projeto..."
                    className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-purple-500"
                />
                <button 
                    onClick={handleAddProject}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold transition-colors flex items-center gap-2"
                >
                    <Plus className="w-4 h-4" /> Adicionar
                </button>
            </div>
            <div className="space-y-2 mt-4">
                {projects.map(p => (
                    <div key={p.id} className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${activeProjectId === p.id ? 'bg-blue-900/20 border-blue-500' : 'bg-slate-900 border-slate-700'}`}>
                        {editingProjectId === p.id ? (
                            <div className="flex-1 flex gap-2 mr-4">
                                <input 
                                    type="text" 
                                    value={editingProjectName}
                                    onChange={(e) => setEditingProjectName(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && saveRenamedProject()}
                                    className="flex-1 bg-slate-950 border border-slate-600 rounded px-2 py-1 text-white text-sm focus:ring-1 focus:ring-blue-500"
                                    autoFocus
                                />
                                <button onClick={saveRenamedProject} className="p-1 text-green-400 hover:bg-slate-800 rounded">
                                    <Check className="w-4 h-4" />
                                </button>
                                <button onClick={cancelEditingProject} className="p-1 text-slate-400 hover:bg-slate-800 rounded">
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        ) : (
                            <span className="font-medium text-white">{p.name}</span>
                        )}
                        
                        <div className="flex gap-2">
                            {editingProjectId !== p.id && (
                                <>
                                    {activeProjectId !== p.id && (
                                        <button 
                                            onClick={() => setActiveProjectId(p.id)}
                                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-sm transition-colors"
                                        >
                                            Selecionar
                                        </button>
                                    )}
                                    <button 
                                        onClick={() => startEditingProject(p)}
                                        className="p-2 text-slate-500 hover:text-blue-400 transition-colors rounded-full hover:bg-slate-800"
                                        title="Renomear Projeto"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                    {p.id !== 'default' && (
                                        <button 
                                            onClick={() => handleDeleteProject(p.id)}
                                            className="p-2 text-slate-500 hover:text-red-400 transition-colors rounded-full hover:bg-slate-800"
                                            title="Excluir Projeto"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
      </section>

      {/* --- EXTERNAL SERVICES (OpenRouter / Grok / OpenAI) --- */}
      <section className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            Serviços Externos (OpenRouter & Premium)
        </h2>
        <p className="text-slate-400 text-sm mb-6">
            Conecte serviços externos para expandir as capacidades do estúdio além do Gemini.
        </p>
        
        <div className="space-y-6">
            {/* OpenRouter (Main Hub) */}
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <label className="block text-sm font-bold text-emerald-400 mb-2 flex items-center gap-2">
                    <Globe className="w-4 h-4" /> OpenRouter (Hub Principal)
                </label>
                <div className="flex gap-2 mb-2">
                    <input 
                        type="password" 
                        placeholder="sk-or-v1-..."
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-emerald-500 outline-none font-mono text-sm"
                        value={settings.openRouterKey || ''}
                        onChange={(e) => handleChange('openRouterKey', e.target.value)}
                    />
                    <button 
                        onClick={handleSyncModels}
                        disabled={isSyncingModels || !settings.openRouterKey}
                        className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                        title="Buscar modelos disponíveis na sua conta"
                    >
                        <RefreshCw className={`w-4 h-4 ${isSyncingModels ? 'animate-spin' : ''}`} />
                        {isSyncingModels ? 'Buscando...' : 'Sincronizar'}
                    </button>
                </div>
                <p className="text-xs text-slate-500 mb-4">
                    Chave única para acessar Flux, Llama 3, DeepSeek, etc. Clique em Sincronizar para ver o que sua chave suporta.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                        <label className="text-xs font-medium text-slate-400 mb-1 block">Modelo de Texto (Roteiros)</label>
                        <select 
                            value={
                                settings.textProvider === 'openai' ? (settings.openaiModel || 'gpt-4o') :
                                settings.textProvider === 'xai' ? (settings.xaiModel || 'grok-2-latest') :
                                settings.textProvider === 'openrouter' ? (settings.openRouterTextModel || '') :
                                'gemini'
                            }
                            onChange={(e) => {
                                const val = e.target.value;
                                if (val === 'gemini') {
                                    handleChange('textProvider', 'gemini');
                                } else if (val.startsWith('gpt')) {
                                    handleChange('textProvider', 'openai');
                                    handleChange('openaiModel', val);
                                } else if (val.startsWith('grok')) {
                                    handleChange('textProvider', 'xai');
                                    handleChange('xaiModel', val);
                                } else {
                                    handleChange('textProvider', 'openrouter');
                                    handleChange('openRouterTextModel', val);
                                }
                            }}
                            className="w-full bg-slate-950 border border-slate-700 rounded px-3 py-2 text-white text-sm"
                        >
                            <option value="gemini">Google Gemini (Padrão - Grátis)</option>
                            
                            <optgroup label="OpenAI (ChatGPT)">
                                <option value="gpt-4o">GPT-4o (Melhor Qualidade)</option>
                                <option value="gpt-4o-mini">GPT-4o Mini (Rápido/Barato)</option>
                            </optgroup>

                            <optgroup label="xAI (Grok)">
                                <option value="grok-2-latest">Grok 2 (Beta)</option>
                            </optgroup>

                            <optgroup label="OpenRouter (Disponíveis)">
                                {availableTextModels.map(model => (
                                    <option key={model.id} value={model.id}>{model.name}</option>
                                ))}
                            </optgroup>
                        </select>
                    </div>
                    {/* Image Model Selector Removed - Focusing on Gemini Ecosystem for Consistency */}
                </div>
            </div>

            {/* Direct Keys (Grok / OpenAI) */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                    <label className="block text-xs font-bold text-slate-400 mb-1 flex items-center gap-2">
                        Chave xAI (Grok)
                    </label>
                    <input
                        type="password"
                        value={settings.xaiKey || ''}
                        onChange={(e) => handleChange('xaiKey', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:ring-2 focus:ring-yellow-500 outline-none text-sm font-mono placeholder-slate-700"
                        placeholder="xai-..."
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-slate-400 mb-1 flex items-center gap-2">
                        Chave OpenAI (ChatGPT)
                    </label>
                    <input
                        type="password"
                        value={settings.openaiKey || ''}
                        onChange={(e) => handleChange('openaiKey', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:ring-2 focus:ring-blue-500 outline-none text-sm font-mono placeholder-slate-700"
                        placeholder="sk-..."
                    />
                </div>
                <div>
                    <label className="block text-xs font-bold text-slate-400 mb-1 flex items-center gap-2">
                        Chave Apify (Web Scraping / Extrator)
                    </label>
                    <input
                        type="password"
                        value={settings.apifyApiKey || ''}
                        onChange={(e) => handleChange('apifyApiKey', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white focus:ring-2 focus:ring-sky-500 outline-none text-sm font-mono placeholder-slate-700"
                        placeholder="apify_api_..."
                    />
                </div>
            </div>
        </div>
      </section>

      {/* --- COMFYUI INTEGRATION --- */}
      <section className="bg-slate-800/50 rounded-xl border border-slate-700 p-6 shadow-lg">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <MonitorPlay className="w-5 h-5 text-indigo-400" />
            Integração ComfyUI (Local / API)
        </h2>
        <p className="text-slate-400 text-sm mb-6">
            Conecte seu ComfyUI local ou remoto para gerar imagens e vídeos diretamente do estúdio.
        </p>
        
        <div className="space-y-6">
            <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50">
                <label className="block text-sm font-bold text-indigo-400 mb-2">
                    URL do Servidor ComfyUI
                </label>
                <div className="flex gap-2">
                    <input 
                        type="text" 
                        placeholder="http://127.0.0.1:8188"
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-sm"
                        value={settings.comfyUrl || ''}
                        onChange={(e) => handleChange('comfyUrl', e.target.value)}
                    />
                    <button 
                        onClick={handleTestComfyUI}
                        disabled={isTestingComfy || !settings.comfyUrl}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                        title="Testar conexão com o ComfyUI"
                    >
                        <Power className={`w-4 h-4 ${isTestingComfy ? 'animate-pulse' : ''}`} />
                        {isTestingComfy ? 'Testando...' : 'Testar Conexão'}
                    </button>
                </div>
                <p className="text-xs text-slate-500 mt-2 mb-4">
                    Certifique-se de que o ComfyUI está rodando e acessível. Se estiver usando remotamente, inclua o protocolo (http/https).
                </p>

                <label className="block text-sm font-bold text-indigo-400 mb-2">
                    API Key / Bearer Token (Opcional)
                </label>
                <div className="flex gap-2">
                    <input 
                        type="password" 
                        placeholder="Insira o token para cloud.comfy.org ou servidores autenticados"
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-sm"
                        value={settings.comfyApiKey || ''}
                        onChange={(e) => handleChange('comfyApiKey', e.target.value)}
                    />
                </div>
                <p className="text-xs text-slate-500 mt-2">
                    Necessário para serviços como ComfyUI Cloud (cloud.comfy.org) ou servidores com autenticação.
                </p>

                <div className="mt-4 bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                    <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                        <AlertCircle className="w-4 h-4 text-indigo-400" />
                        Onde encontro a URL e a API Key?
                    </h4>
                    <ul className="text-xs text-slate-400 space-y-2 list-disc list-inside">
                        <li>
                            <strong className="text-slate-300">ComfyUI Local:</strong> A URL padrão é <code className="bg-slate-900 px-1 py-0.5 rounded text-indigo-300">http://127.0.0.1:8188</code>. Deixe a API Key em branco.
                        </li>
                        <li>
                            <strong className="text-slate-300">ComfyUI Cloud:</strong> Crie uma conta em <a href="https://platform.comfy.org" target="_blank" rel="noreferrer" className="text-indigo-400 hover:underline">platform.comfy.org</a>. A URL da API é <code className="bg-slate-900 px-1 py-0.5 rounded text-indigo-300">https://cloud.comfy.org</code>. A API Key pode ser gerada em <em>Profile &gt; API Keys</em>.
                        </li>
                        <li>
                            <strong className="text-slate-300">RunPod / Modal:</strong> Use a URL pública fornecida pelo serviço (ex: <code className="bg-slate-900 px-1 py-0.5 rounded text-indigo-300">https://&lt;id&gt;-8188.proxy.runpod.net</code>). A API Key geralmente não é necessária, a menos que você tenha configurado autenticação básica.
                        </li>
                    </ul>
                </div>
            </div>

            <div className="mt-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-md font-bold text-slate-300">Workflows Salvos</h3>
                    <div className="flex gap-2">
                        <label className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-colors cursor-pointer">
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                            Importar
                            <input 
                                type="file" 
                                accept=".json" 
                                className="hidden" 
                                onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (!file) return;
                                    const reader = new FileReader();
                                    reader.onload = (event) => {
                                        try {
                                            const imported = JSON.parse(event.target?.result as string);
                                            if (Array.isArray(imported)) {
                                                // Ensure they have new IDs to avoid conflicts
                                                const newWorkflows = imported.map(w => ({ ...w, id: crypto.randomUUID() }));
                                                handleChange('comfyWorkflows', [...(settings.comfyWorkflows || []), ...newWorkflows]);
                                                toast.success(`${newWorkflows.length} workflows importados!`);
                                            } else {
                                                toast.error("Formato inválido. Esperado um array de workflows.");
                                            }
                                        } catch {
                                            toast.error("Erro ao ler o arquivo JSON.");
                                        }
                                    };
                                    reader.readAsText(file);
                                    e.target.value = ''; // Reset input
                                }}
                            />
                        </label>
                        <button
                            onClick={() => {
                                if (!settings.comfyWorkflows || settings.comfyWorkflows.length === 0) {
                                    toast.error("Nenhum workflow para exportar.");
                                    return;
                                }
                                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(settings.comfyWorkflows, null, 2));
                                const downloadAnchorNode = document.createElement('a');
                                downloadAnchorNode.setAttribute("href",     dataStr);
                                downloadAnchorNode.setAttribute("download", "workflows_comfyui.json");
                                document.body.appendChild(downloadAnchorNode); // required for firefox
                                downloadAnchorNode.click();
                                downloadAnchorNode.remove();
                            }}
                            className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-colors"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2-2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                            Exportar
                        </button>
                        <button
                            onClick={() => {
                                setEditingWorkflow({ id: crypto.randomUUID(), name: 'Novo Workflow', type: 'image', json: '' });
                            }}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-1.5 rounded text-sm font-medium flex items-center gap-2 transition-colors"
                        >
                            <Plus className="w-4 h-4" /> Adicionar
                        </button>
                    </div>
                </div>

                {settings.comfyWorkflows && settings.comfyWorkflows.length > 0 && (
                    <div className="mb-4">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Buscar workflows por nome ou categoria..."
                                value={workflowSearchQuery}
                                onChange={(e) => setWorkflowSearchQuery(e.target.value)}
                                className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition-colors"
                            />
                            <svg className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                            {workflowSearchQuery && (
                                <button 
                                    onClick={() => setWorkflowSearchQuery('')}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            )}
                        </div>
                    </div>
                )}

                {settings.comfyWorkflows && settings.comfyWorkflows.length > 0 ? (
                    <div className="space-y-6">
                        {(() => {
                            const filteredWorkflows = settings.comfyWorkflows.filter(wf => 
                                !workflowSearchQuery || 
                                wf.name.toLowerCase().includes(workflowSearchQuery.toLowerCase()) || 
                                (wf.category && wf.category.toLowerCase().includes(workflowSearchQuery.toLowerCase()))
                            );

                            if (filteredWorkflows.length === 0) {
                                return (
                                    <div className="text-center py-8 text-slate-500 bg-slate-800/30 rounded-lg border border-slate-700/50">
                                        Nenhum workflow encontrado para "{workflowSearchQuery}".
                                    </div>
                                );
                            }

                            return Object.entries(
                                filteredWorkflows.reduce((acc, wf) => {
                                    const cat = wf.category || 'Sem Categoria';
                                    if (!acc[cat]) acc[cat] = [];
                                    acc[cat].push(wf);
                                    return acc;
                                }, {} as Record<string, typeof settings.comfyWorkflows>)
                            ).sort(([a], [b]) => a === 'Sem Categoria' ? 1 : b === 'Sem Categoria' ? -1 : a.localeCompare(b))
                            .map(([category, workflows]) => (
                                <div key={category}>
                                    <h4 className="text-sm font-bold text-slate-400 mb-3 border-b border-slate-700/50 pb-1">{category}</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {workflows.map(wf => (
                                        <div key={wf.id} className="bg-slate-900/50 p-4 rounded-lg border border-slate-700/50 flex justify-between items-start">
                                            <div className="flex-1 min-w-0 pr-4">
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${wf.type === 'image' ? 'bg-blue-500/20 text-blue-400' : 'bg-purple-500/20 text-purple-400'}`}>
                                                        {wf.type === 'image' ? 'Imagem' : 'Vídeo'}
                                                    </span>
                                                    <h4 className="font-bold text-slate-200 truncate">{wf.name}</h4>
                                                </div>
                                                <p className="text-xs text-slate-500 line-clamp-2 font-mono mt-2 break-all">{wf.json.substring(0, 100)}...</p>
                                            </div>
                                            <div className="flex gap-2 flex-shrink-0">
                                                <button 
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(wf.json);
                                                        toast.success("JSON copiado!");
                                                    }} 
                                                    className="p-1.5 text-slate-400 hover:text-green-400 hover:bg-slate-700 rounded transition-colors"
                                                    title="Copiar JSON"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                                </button>
                                                <button onClick={() => setEditingWorkflow(wf)} className="p-1.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors" title="Editar">
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                                <button 
                                                    onClick={() => {
                                                        const newWf = { ...wf, id: crypto.randomUUID(), name: `${wf.name} (Cópia)` };
                                                        handleChange('comfyWorkflows', [...(settings.comfyWorkflows || []), newWf]);
                                                    }} 
                                                    className="p-1.5 text-slate-400 hover:text-blue-400 hover:bg-slate-700 rounded transition-colors"
                                                    title="Duplicar"
                                                >
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                                                </button>
                                                <button 
                                                    onClick={() => {
                                                        handleChange('comfyWorkflows', settings.comfyWorkflows?.filter(w => w.id !== wf.id));
                                                    }} 
                                                    className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-700 rounded transition-colors"
                                                    title="Remover"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))
                        })()}
                    </div>
                ) : (
                    <div className="text-center py-8 bg-slate-900/30 rounded-lg border border-slate-700/30 border-dashed">
                        <p className="text-slate-500 text-sm">Nenhum workflow salvo. Adicione um para começar.</p>
                    </div>
                )}

                {/* Modal for editing workflow */}
                {editingWorkflow && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                        <div className="bg-slate-800 rounded-xl p-6 w-full max-w-2xl border border-slate-700 shadow-2xl">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-xl font-bold text-white">
                                    {settings.comfyWorkflows?.some(w => w.id === editingWorkflow.id) ? 'Editar Workflow' : 'Novo Workflow'}
                                </h3>
                                <button onClick={() => setEditingWorkflow(null)} className="text-slate-400 hover:text-white">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="space-y-4">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-300 mb-1">Nome do Workflow</label>
                                        <input 
                                            type="text" 
                                            value={editingWorkflow.name}
                                            onChange={e => setEditingWorkflow({...editingWorkflow, name: e.target.value})}
                                            className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                                            placeholder="Ex: SDXL Turbo + LoRA Anime"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-300 mb-1">Categoria / Tag (Opcional)</label>
                                        <input 
                                            type="text" 
                                            value={editingWorkflow.category || ''}
                                            onChange={e => setEditingWorkflow({...editingWorkflow, category: e.target.value})}
                                            className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none"
                                            placeholder="Ex: Anime, Realista, Rascunho"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">Tipo</label>
                                    <div className="flex gap-4">
                                        <label className="flex items-center gap-2 cursor-pointer">
                                            <input 
                                                type="radio" 
                                                checked={editingWorkflow.type === 'image'}
                                                onChange={() => setEditingWorkflow({...editingWorkflow, type: 'image'})}
                                                className="text-indigo-500 focus:ring-indigo-500 bg-slate-900 border-slate-600"
                                            />
                                            <span className="text-slate-300">Imagem (T2I / I2I)</span>
                                        </label>
                                        <label className="flex items-center gap-2 cursor-pointer">
                                            <input 
                                                type="radio" 
                                                checked={editingWorkflow.type === 'video'}
                                                onChange={() => setEditingWorkflow({...editingWorkflow, type: 'video'})}
                                                className="text-indigo-500 focus:ring-indigo-500 bg-slate-900 border-slate-600"
                                            />
                                            <span className="text-slate-300">Vídeo (I2V / T2V)</span>
                                        </label>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-300 mb-1">JSON API do ComfyUI</label>
                                    <textarea 
                                        value={editingWorkflow.json}
                                        onChange={e => setEditingWorkflow({...editingWorkflow, json: e.target.value})}
                                        className="w-full h-64 bg-slate-950 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-xs resize-none"
                                        placeholder='{"3": {"class_type": "KSampler", ...}}'
                                    />
                                </div>

                                <div className="flex justify-end gap-3 mt-6">
                                    <button 
                                        onClick={() => setEditingWorkflow(null)}
                                        className="px-4 py-2 text-slate-300 hover:text-white transition-colors"
                                    >
                                        Cancelar
                                    </button>
                                    <button 
                                        onClick={() => {
                                            if (!editingWorkflow.name.trim() || !editingWorkflow.json.trim()) {
                                                toast.error("Preencha o nome e o JSON.");
                                                return;
                                            }
                                            try {
                                                JSON.parse(editingWorkflow.json);
                                            } catch {
                                                toast.error("O JSON inserido é inválido.");
                                                return;
                                            }

                                            const currentWorkflows = settings.comfyWorkflows || [];
                                            const exists = currentWorkflows.some(w => w.id === editingWorkflow.id);
                                            
                                            let newWorkflows;
                                            if (exists) {
                                                newWorkflows = currentWorkflows.map(w => w.id === editingWorkflow.id ? editingWorkflow : w);
                                            } else {
                                                newWorkflows = [...currentWorkflows, editingWorkflow];
                                            }
                                            
                                            handleChange('comfyWorkflows', newWorkflows);
                                            setEditingWorkflow(null);
                                            toast.success("Workflow salvo!");
                                        }}
                                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                                    >
                                        Salvar Workflow
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Modal for viewing document */}
                {viewingDocument && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
                        <div className="bg-slate-800 rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col border border-slate-700 shadow-2xl overflow-hidden">
                            <div className="flex justify-between items-center p-4 border-b border-slate-700 bg-slate-800/50">
                                <div className="flex items-center gap-2 text-white">
                                    <FileText className="w-5 h-5 text-indigo-400" />
                                    <h3 className="text-lg font-bold truncate max-w-md">{viewingDocument.name}</h3>
                                </div>
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={handleSummarizeDocument}
                                        disabled={isSummarizing}
                                        className="bg-amber-600/20 hover:bg-amber-600/30 text-amber-500 border border-amber-600/50 hover:border-amber-500 px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
                                        title="Usa a IA (Gemini Base) para ler todo o documento e extrair apenas as regras essenciais, economizando muitos tokens."
                                    >
                                        {isSummarizing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Brain className="w-4 h-4" />}
                                        {isSummarizing ? 'Resumindo...' : '✨ Extrair Essência (IA)'}
                                    </button>
                                    <button onClick={() => setViewingDocument(null)} className="text-slate-400 hover:text-white p-1 bg-slate-700/50 hover:bg-slate-700 rounded transition-colors">
                                        <X className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>

                            <div className="flex-1 p-4 overflow-y-auto bg-slate-900">
                                <textarea
                                    value={viewingDocument.content}
                                    onChange={(e) => {
                                        setViewingDocument({...viewingDocument, content: e.target.value});
                                    }}
                                    className="w-full h-full min-h-[500px] bg-slate-950 border border-slate-700 rounded-lg p-4 text-slate-300 font-mono text-sm resize-none outline-none focus:ring-1 focus:ring-indigo-500"
                                />
                            </div>
                            <div className="p-4 border-t border-slate-700 bg-slate-800 flex justify-end">
                                <button
                                    onClick={() => {
                                        const newKnowledge = (settings.knowledgeBase || []).map(d => d.id === viewingDocument.id ? viewingDocument : d);
                                        handleChange('knowledgeBase', newKnowledge);
                                        setViewingDocument(null);
                                        toast.success("Documento atualizado!");
                                    }}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg font-bold transition-colors shadow-lg"
                                >
                                    Salvar Alterações
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
      </section>

      {/* Global Config */}
      <div>
        <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
               Configurações do Canal Atual
            </h2>
            <div className="flex gap-2">
                 <button 
                    onClick={() => {
                        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ settings, apiKeys }, null, 2));
                        const downloadAnchorNode = document.createElement('a');
                        downloadAnchorNode.setAttribute("href", dataStr);
                        downloadAnchorNode.setAttribute("download", "gemini_studio_backup.json");
                        document.body.appendChild(downloadAnchorNode);
                        downloadAnchorNode.click();
                        downloadAnchorNode.remove();
                    }}
                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded border border-slate-600 flex items-center gap-2 transition-colors"
                >
                    <Save className="w-3 h-3" /> Backup Config
                </button>
                <label className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded border border-slate-600 flex items-center gap-2 transition-colors cursor-pointer">
                    <Upload className="w-3 h-3" /> Restaurar
                    <input 
                        type="file" 
                        className="hidden" 
                        accept=".json"
                        onChange={(e) => {
                            const file = e.target.files?.[0];
                            if (!file) return;
                            const reader = new FileReader();
                            reader.onload = (event) => {
                                try {
                                    const data = JSON.parse(event.target?.result as string);
                                    if (data.settings) setSettings(data.settings);
                                    if (data.apiKeys) setApiKeys(data.apiKeys);
                                    toast.success("Configurações restauradas com sucesso!");
                                } catch (_err) {
                                    console.error(_err);
                                    toast.error("Erro ao ler arquivo de backup.");
                                }
                            };
                            reader.readAsText(file);
                        }}
                    />
                </label>
            </div>
        </div>

        <p className="text-slate-400 text-sm mb-6">
            Estas configurações são salvas automaticamente para o canal selecionado ({projects.find(p => p.id === activeProjectId)?.name || 'Padrão'}).
        </p>

        {/* Channel Personalization Section */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 space-y-4 mb-6">
            <h3 className="text-md font-bold text-slate-200 flex items-center gap-2">
                <Palette className="w-4 h-4 text-pink-400" />
                Personalização Visual do Canal
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Icon Selection */}
                <div>
                    <label className="block text-sm font-bold text-slate-400 mb-2">Ícone do Canal</label>
                    <div className="flex flex-wrap gap-2">
                        {PROJECT_ICONS.map(iconName => {
                            const isActive = (projects.find(p => p.id === activeProjectId)?.icon || 'Layout') === iconName;
                            return (
                                <button
                                    key={iconName}
                                    onClick={() => {
                                        setProjects(prev => prev.map(p => p.id === activeProjectId ? { ...p, icon: iconName } : p));
                                    }}
                                    className={`p-2 rounded-lg border transition-all ${isActive ? 'bg-slate-700 border-slate-400 text-white' : 'bg-slate-900 border-slate-700 text-slate-500 hover:bg-slate-800 hover:text-slate-300'}`}
                                    title={iconName}
                                >
                                    {getIconComponent(iconName)}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Color Selection */}
                <div>
                    <label className="block text-sm font-bold text-slate-400 mb-2">Cor do Canal</label>
                    <div className="flex flex-wrap gap-2">
                        {PROJECT_COLORS.map(color => {
                            const isActive = (projects.find(p => p.id === activeProjectId)?.color || 'blue') === color.id;
                            return (
                                <button
                                    key={color.id}
                                    onClick={() => {
                                        setProjects(prev => prev.map(p => p.id === activeProjectId ? { ...p, color: color.id } : p));
                                    }}
                                    className={`w-8 h-8 rounded-full transition-all ${color.class} ${isActive ? 'ring-2 ring-white ring-offset-2 ring-offset-slate-900' : 'opacity-50 hover:opacity-100'}`}
                                    title={color.id}
                                />
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
        
        {/* Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                    Motor de Imagem
                </label>
                <select
                    value={settings.imageProvider || 'gemini'}
                    onChange={(e) => handleChange('imageProvider', e.target.value as any)}
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                >
                    <option value="gemini">Google Gemini (Nativo)</option>
                    <option value="comfyui">ComfyUI (Local/API)</option>
                    <option value="flux_modal">FLUX Dev 8-bit (Modal - Estilo)</option>
                    <option value="flux_pulid">FLUX Dev 8-bit (PuLID - Face ID)</option>
                    <option value="apollo-cloud-multipass">Apollo Cloud (Multi-Pass AI)</option>
                </select>
                
                {settings.imageProvider === 'comfyui' && (
                    <div className="mt-2">
                        <label className="block text-xs font-medium text-slate-500 mb-1">
                            Workflow de Imagem
                        </label>
                        <select
                            value={projects.find(p => p.id === activeProjectId)?.defaultImageWorkflowId || ''}
                            onChange={(e) => {
                                setProjects(prev => prev.map(p => 
                                    p.id === activeProjectId ? { ...p, defaultImageWorkflowId: e.target.value } : p
                                ));
                            }}
                            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white focus:ring-1 focus:ring-indigo-500 outline-none text-sm"
                        >
                            <option value="">Selecione um workflow...</option>
                            {settings.comfyWorkflows?.filter(w => w.type === 'image').map(w => (
                                <option key={w.id} value={w.id}>{w.name}</option>
                            ))}
                        </select>
                    </div>
                )}
            </div>
            <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">
                    Motor de Vídeo
                </label>
                <select
                    value={settings.videoProvider || 'gemini'}
                    onChange={(e) => handleChange('videoProvider', e.target.value as any)}
                    className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
                >
                    <option value="gemini">Google Veo (Nativo)</option>
                    <option value="comfyui">ComfyUI (Local/API)</option>
                </select>
                
                {settings.videoProvider === 'comfyui' && (
                    <div className="mt-2">
                        <label className="block text-xs font-medium text-slate-500 mb-1">
                            Workflow de Vídeo
                        </label>
                        <select
                            value={projects.find(p => p.id === activeProjectId)?.defaultVideoWorkflowId || ''}
                            onChange={(e) => {
                                setProjects(prev => prev.map(p => 
                                    p.id === activeProjectId ? { ...p, defaultVideoWorkflowId: e.target.value } : p
                                ));
                            }}
                            className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white focus:ring-1 focus:ring-indigo-500 outline-none text-sm"
                        >
                            <option value="">Selecione um workflow...</option>
                            {settings.comfyWorkflows?.filter(w => w.type === 'video').map(w => (
                                <option key={w.id} value={w.id}>{w.name}</option>
                            ))}
                        </select>
                    </div>
                )}
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-400 mb-1">
              Modelo Padrão (Gemini)
            </label>
            <select
              value={settings.modelId}
              onChange={(e) => handleChange('modelId', e.target.value)}
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
            >
              {MODELS.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1">
              Resolução (Nano Banana 2)
            </label>
            <select
              value={settings.imageSize || '1K'}
              onChange={(e) => handleChange('imageSize', e.target.value)}
              className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
            >
              <option value="1K">1K (Padrão)</option>
              <option value="2K">2K (Alta)</option>
              <option value="4K">4K (Ultra)</option>
            </select>
          </div>

          <div className="flex items-end text-sm text-slate-500 pb-2 md:col-span-3">
              Nota: As configurações de Proporção estão localizadas na aba "Auto Execução". Resolução 2K/4K funciona apenas com o modelo Nano Banana 2.
          </div>
        </div>

        {/* High Thinking Toggle */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 mb-6 flex items-center justify-between">
            <div>
                <h3 className="text-md font-bold text-slate-200 flex items-center gap-2">
                    <Brain className="w-4 h-4 text-purple-400" />
                    Modo de Raciocínio Profundo (High Thinking)
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                    Usa o modelo gemini-3.1-pro-preview para gerar roteiros complexos e melhorar prompts como um Diretor de Arte.
                </p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
                <input 
                    type="checkbox" 
                    className="sr-only peer"
                    checked={settings.useThinking || false}
                    onChange={(e) => handleChange('useThinking', e.target.checked)}
                />
                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
        </div>

        {/* OpenAI Rewrite Extension Integration */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 mb-6">
            <h3 className="text-md font-bold text-slate-200 flex items-center gap-2 mb-2">
                <Key className="w-4 h-4 text-green-400" />
                Chave API OpenAI (Auto VEO/FLOW Anti-Censura)
            </h3>
            <p className="text-xs text-slate-400 mb-4">
                Esta chave será usada exclusivamente pela extensão Auto VEO/FLOW para reescrever comandos censurados automaticamente no background usando o ChatGPT (modifica a tag na hora).
            </p>
            <input 
                type="password" 
                value={settings.openaiKey || ''}
                onChange={(e) => {
                    handleChange('openaiKey', e.target.value);
                    // Also save to localStorage for the extension to pick up in its own way if needed
                    window.localStorage.setItem('openai_api_key', e.target.value.trim());
                }}
                placeholder="sk-proj-..."
                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-green-500 outline-none font-mono text-sm"
            />
        </div>

        {/* Context & Style Section */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 space-y-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-md font-bold text-slate-200 flex items-center gap-2">
                    <Globe className="w-4 h-4 text-orange-400" />
                    Contexto & Direção de Arte
                </h3>
                <div className="flex items-center gap-2">
                    <select 
                        className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-sm text-white focus:ring-1 focus:ring-purple-500 outline-none"
                        value={activeProject?.activePresetId || ''}
                        onChange={(e) => {
                            const presetId = e.target.value;
                            setProjects(prev => prev.map(p => p.id === activeProjectId ? { ...p, activePresetId: presetId || undefined } : p));
                        }}
                    >
                        <option value="">Padrão do Canal</option>
                        {activeProject?.presets?.map(preset => (
                            <option key={preset.id} value={preset.id}>{preset.name}</option>
                        ))}
                    </select>
                    <button 
                        onClick={() => {
                            const name = prompt("Nome do novo preset:");
                            if (name) {
                                const newPreset = {
                                    id: crypto.randomUUID(),
                                    name,
                                    globalContext: settings.globalContext || '',
                                    sceneContext: settings.sceneContext || '',
                                    negativePrompt: settings.negativePrompt || '',
                                    styleReferenceImage: settings.styleReferenceImage
                                };
                                setProjects(prev => prev.map(p => p.id === activeProjectId ? { 
                                    ...p, 
                                    presets: [...(p.presets || []), newPreset],
                                    activePresetId: newPreset.id
                                } : p));
                            }
                        }}
                        className="bg-slate-700 hover:bg-slate-600 text-white px-3 py-1 rounded text-sm transition-colors"
                    >
                        Salvar Preset
                    </button>
                    {activeProject?.activePresetId && (
                        <button 
                            onClick={() => {
                                setProjects(prev => prev.map(p => p.id === activeProjectId ? {
                                    ...p,
                                    presets: p.presets?.filter(preset => preset.id !== p.activePresetId),
                                    activePresetId: undefined
                                } : p));
                            }}
                            className="bg-red-900/50 hover:bg-red-900 text-red-200 px-3 py-1 rounded text-sm transition-colors"
                        >
                            Excluir
                        </button>
                    )}
                </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Global Style */}
                <div>
                    <label className="block text-sm font-bold text-slate-400 mb-1 flex items-center gap-2">
                        <Palette className="w-3 h-3" /> Estilo Visual Global (Texto)
                    </label>
                    <textarea
                        value={settings.globalContext}
                        onChange={(e) => handleChange('globalContext', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none h-24 text-sm resize-none placeholder-slate-600"
                        placeholder="Ex: Fantasia Sombria, Iluminação Cinematográfica, Estilo Pixar, Grão de Filme, Cores Pastéis..."
                    />
                    <p className="text-xs text-slate-500 mt-1">Define a aparência artística de todas as imagens geradas.</p>
                </div>

                {/* Brand Kit */}
                <div className="pt-4 border-t border-slate-700">
                    <h3 className="text-md font-bold text-white mb-3 flex items-center gap-2">
                        <Palette className="w-4 h-4 text-indigo-400" /> Kit de Marca (Brand Kit)
                    </h3>
                    
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-bold text-slate-400 mb-1">Cores da Marca (Hex)</label>
                            <div className="flex gap-2 flex-wrap">
                                {(settings.brandKit?.colors || []).map((color, i) => (
                                    <div key={i} className="flex items-center gap-1 bg-slate-900 border border-slate-700 rounded px-2 py-1">
                                        <div className="w-4 h-4 rounded-full border border-slate-600" style={{ backgroundColor: color }} />
                                        <span className="text-xs text-slate-300">{color}</span>
                                        <button 
                                            onClick={() => {
                                                const newColors = [...(settings.brandKit?.colors || [])];
                                                newColors.splice(i, 1);
                                                handleChange('brandKit', { ...settings.brandKit, colors: newColors });
                                            }}
                                            className="text-slate-500 hover:text-red-400 ml-1"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                ))}
                                <button
                                    onClick={() => {
                                        const color = prompt("Digite a cor em Hex (ex: #FF5500):");
                                        if (color && /^#[0-9A-F]{6}$/i.test(color)) {
                                            handleChange('brandKit', { 
                                                ...settings.brandKit, 
                                                colors: [...(settings.brandKit?.colors || []), color] 
                                            });
                                        } else if (color) {
                                            toast.error("Formato inválido. Use #HEX.");
                                        }
                                    }}
                                    className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded border border-slate-600 flex items-center gap-1 transition-colors"
                                >
                                    <Plus className="w-3 h-3" /> Adicionar Cor
                                </button>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-bold text-slate-400 mb-1">Fonte Principal</label>
                            <input
                                type="text"
                                value={settings.brandKit?.fontFamily || ''}
                                onChange={(e) => handleChange('brandKit', { ...settings.brandKit, fontFamily: e.target.value, colors: settings.brandKit?.colors || [] })}
                                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none text-sm"
                                placeholder="Ex: Montserrat, Inter, Roboto..."
                            />
                        </div>
                    </div>
                </div>

                {/* Knowledge Base */}
                <div className="pt-4 border-t border-slate-700">
                    <h3 className="text-md font-bold text-white mb-3 flex items-center gap-2">
                        <BookOpen className="w-4 h-4 text-indigo-400" /> Base de Conhecimento (RAG)
                    </h3>
                    <p className="text-xs text-slate-400 mb-4">
                        Adicione textos, roteiros antigos ou diretrizes do canal. A IA usará isso como contexto para gerar conteúdos (roteiros, legendas) com a sua identidade.
                    </p>
                    
                    <div className="space-y-3">
                        {(!settings.knowledgeBase || settings.knowledgeBase.length === 0) && (
                            <div className="text-center py-6 bg-slate-900/30 rounded-lg border border-slate-700/30 border-dashed">
                                <p className="text-slate-500 text-xs">Nenhum documento na Base de Dados interna deste canal.</p>
                            </div>
                        )}
                        {(settings.knowledgeBase || []).map((doc) => (
                            <div key={doc.id} className="bg-slate-900 border border-slate-700 rounded-lg p-3 flex justify-between items-center group">
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <FileText className="w-5 h-5 text-slate-500 flex-shrink-0" />
                                    <div className="truncate">
                                        <p className="text-sm font-medium text-slate-200 truncate">{doc.name}</p>
                                        <p className="text-xs text-slate-500">{Math.round(doc.content.length / 1024)} KB</p>
                                    </div>
                                </div>
                                <div className="flex items-center">
                                    <button
                                        onClick={() => setViewingDocument(doc)}
                                        className="p-2 text-slate-400 hover:text-indigo-400 hover:bg-slate-800 rounded-lg transition-colors"
                                        title="Visualizar documento"
                                    >
                                        <Eye className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={() => {
                                            handleChange('knowledgeBase', (settings.knowledgeBase || []).filter(d => d.id !== doc.id));
                                        }}
                                        className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-lg transition-colors"
                                        title="Remover documento"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}

                        <label className="flex items-center justify-center w-full py-3 border-2 border-slate-700 border-dashed rounded-lg cursor-pointer bg-slate-900 hover:bg-slate-800 transition-colors text-sm font-medium text-slate-300 gap-2">
                            <Plus className="w-4 h-4" /> Adicionar Documento (.txt)
                            <input 
                                type="file" 
                                accept=".txt,.md,.json"
                                className="hidden"
                                onChange={(e) => {
                                    const file = e.target.files?.[0];
                                    if (!file) return;

                                    const reader = new FileReader();
                                    reader.onload = (event) => {
                                        const content = event.target?.result as string;
                                        const newDoc = {
                                            id: crypto.randomUUID(),
                                            name: file.name,
                                            content: content
                                        };
                                        handleChange('knowledgeBase', [...(settings.knowledgeBase || []), newDoc]);
                                        toast.success(`Documento "${file.name}" adicionado!`);
                                    };
                                    reader.readAsText(file);
                                    e.target.value = ''; // Reset input
                                }}
                            />
                        </label>

                        <div className="flex gap-2 items-center mt-4">
                            <input
                                type="text"
                                placeholder="Ou cole a URL de um site para extrair texto via Apify..."
                                value={scrapingUrl}
                                onChange={(e) => setScrapingUrl(e.target.value)}
                                className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-white focus:ring-2 focus:ring-sky-500 outline-none text-sm placeholder-slate-500"
                            />
                            <button
                                onClick={handleScrapeUrl}
                                disabled={isScraping || !scrapingUrl.trim()}
                                className="bg-sky-600 hover:bg-sky-700 disabled:opacity-50 text-white p-2 rounded-lg transition-colors flex items-center justify-center"
                                title="Extrair site e adicionar"
                            >
                                {isScraping ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Style Reference Image */}
                <div className="pt-4 border-t border-slate-700">
                    <label className="block text-sm font-bold text-slate-400 mb-1 flex items-center gap-2">
                        <ImageIcon className="w-3 h-3" /> Imagem de Referência de Estilo Global
                    </label>
                    {settings.styleReferenceImage ? (
                        <div className="relative w-full h-32 rounded-lg overflow-hidden border border-slate-600 group">
                            <img src={settings.styleReferenceImage} alt="Style Reference" className="w-full h-full object-cover" />
                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                <button
                                    onClick={() => handleChange('styleReferenceImage', undefined)}
                                    className="p-2 bg-red-500/80 hover:bg-red-500 text-white rounded-full transition-colors"
                                    title="Remover Imagem de Referência"
                                >
                                    <X className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-slate-600 border-dashed rounded-lg cursor-pointer bg-slate-900 hover:bg-slate-800 transition-colors">
                            <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                <ImageIcon className="w-8 h-8 mb-2 text-slate-500" />
                                <p className="text-sm text-slate-400"><span className="font-semibold text-purple-400">Clique para enviar</span> ou arraste</p>
                                <p className="text-xs text-slate-500 mt-1">A IA copiará o estilo, não o conteúdo.</p>
                            </div>
                            <input 
                                type="file" 
                                className="hidden" 
                                accept="image/*"
                                onChange={async (e) => {
                                    const file = e.target.files?.[0];
                                    if (file) {
                                        try {
                                            const resizedBase64 = await resizeImage(file, 512, 512);
                                            handleChange('styleReferenceImage', resizedBase64);
                                        } catch {
                                            toast.error("Erro ao processar a imagem.");
                                        }
                                    }
                                }}
                            />
                        </label>
                    )}
                    <p className="text-xs text-slate-500 mt-1">Força TODAS as imagens geradas a seguirem a estética visual desta imagem (cores, traço, iluminação).</p>
                </div>

                {/* Scene Context */}
                <div>
                    <label className="block text-sm font-bold text-slate-400 mb-1 flex items-center gap-2">
                        <Layers className="w-3 h-3" /> Contexto da Cena (Lote Atual)
                    </label>
                    <textarea
                        value={settings.sceneContext}
                        onChange={(e) => handleChange('sceneContext', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none h-24 text-sm resize-none placeholder-slate-600"
                        placeholder="Ex: Floresta chuvosa à noite, neblina densa, ruínas antigas ao fundo..."
                    />
                    <p className="text-xs text-slate-500 mt-1">Define o ambiente/cenário. Essencial para manter a consistência do fundo em um lote de imagens.</p>
                </div>

                {/* Negative Prompt (Global) */}
                <div className="md:col-span-2">
                    <label className="block text-sm font-bold text-slate-400 mb-1 flex items-center gap-2">
                        <ShieldCheck className="w-3 h-3 text-red-400" /> Prompt Negativo Global
                    </label>
                    <input
                        type="text"
                        value={settings.negativePrompt || ''}
                        onChange={(e) => handleChange('negativePrompt', e.target.value)}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-red-500 outline-none text-sm placeholder-slate-600"
                        placeholder="Ex: Texto, marca d'água, deformado, baixa qualidade..."
                    />
                    <p className="text-xs text-slate-500 mt-1">Elementos que devem ser evitados em TODAS as gerações.</p>
                </div>

                {/* Grounding Toggle */}
                <div className="md:col-span-2">
                    <div 
                        onClick={() => handleChange('useGrounding', !settings.useGrounding)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-3 ${settings.useGrounding ? 'bg-blue-900/20 border-blue-500' : 'bg-slate-900 border-slate-700 hover:bg-slate-800'}`}
                    >
                        <div className={`w-5 h-5 rounded border flex items-center justify-center ${settings.useGrounding ? 'bg-blue-500 border-blue-400' : 'border-slate-500'}`}>
                            {settings.useGrounding && <Globe className="w-3 h-3 text-white" />}
                        </div>
                        <div>
                            <span className={`text-sm font-bold block ${settings.useGrounding ? 'text-blue-300' : 'text-slate-400'}`}>Ativar Grounding (Busca Google)</span>
                            <span className="text-xs text-slate-500 block">Permite que a IA use dados reais da web para gerar objetos e locais com maior precisão (Apenas modelos suportados).</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        {/* Presets Section */}
        <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700 space-y-4 mt-6">
            <h3 className="text-md font-bold text-slate-200 flex items-center gap-2">
                <Bookmark className="w-4 h-4 text-purple-400" />
                Presets de Configuração
            </h3>
            
            <div className="flex gap-2 mb-4">
                <input
                    type="text"
                    value={newPresetName}
                    onChange={(e) => setNewPresetName(e.target.value)}
                    placeholder="Nome do novo preset..."
                    className="flex-1 bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none text-sm"
                />
                <button
                    onClick={handleSavePreset}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded font-medium flex items-center gap-2 transition-colors text-sm shrink-0"
                >
                    <Save className="w-4 h-4" /> Salvar Atual
                </button>
            </div>

            {activeProject?.presets && activeProject.presets.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {activeProject.presets.map(preset => (
                        <div key={preset.id} className={`bg-slate-900 border ${activeProject.activePresetId === preset.id ? 'border-purple-500' : 'border-slate-700'} rounded-lg p-3 flex justify-between items-center group`}>
                            <span className="text-sm font-medium text-slate-300 truncate pr-2" title={preset.name}>
                                {preset.name} {activeProject.activePresetId === preset.id && '(Ativo)'}
                            </span>
                            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                <button
                                    onClick={() => handleLoadPreset(preset)}
                                    className="p-1.5 bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white rounded transition-colors"
                                    title="Ativar Preset"
                                >
                                    <Upload className="w-3.5 h-3.5" />
                                </button>
                                <button
                                    onClick={() => handleDeletePreset(preset.id)}
                                    className="p-1.5 bg-red-600/20 text-red-400 hover:bg-red-600 hover:text-white rounded transition-colors"
                                    title="Excluir Preset"
                                >
                                    <Trash2 className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                    <p className="text-sm text-slate-400 mb-2"><strong>O que são Presets?</strong></p>
                    <p className="text-xs text-slate-500">
                        Eles salvam a combinação exata de "Direção de Arte", "Contexto Narrativo" e "Prompt Negativo" que você preencheu acima.
                        Perfeito se você quiser ter variações rápidas de estilo (ex: "Versão Sombria", "Versão Cartoon") dentro do mesmo canal, sem precisar reescrever as caixas de texto toda vez.
                    </p>
                </div>
            )}
        </div>

      </div>

      <hr className="border-slate-700" />

      {/* API Key Manager */}
      <div>
        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          <Key className="w-5 h-5 text-yellow-400" />
          Cofre de Chaves Google Gemini
        </h2>
        <div className="flex justify-between items-start mb-4">
            <p className="text-sm text-slate-400 max-w-2xl">
              Gerencie seu pool de rotação. Se uma chave atingir um limite de taxa (contagem de erros aumentar), você pode desativá-la ou aguardar e redefini-la.
            </p>
            <button 
                onClick={() => {
                    setApiKeys(prev => prev.map(k => ({...k, isRateLimited: false, errorCount: 0, rateLimitedUntil: 0})));
                }}
                className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-600 px-3 py-1.5 rounded flex items-center gap-2 transition-colors"
                title="Forçar desbloqueio de todas as chaves (Use se o bloqueio for incorreto)"
            >
                <RefreshCw className="w-3 h-3" /> Resetar Status
            </button>
        </div>

        <div className="flex flex-col md:flex-row gap-2 mb-6 items-end">
          <div className="flex-1">
              <label className="text-xs text-slate-400 mb-1 block">Apelido</label>
              <input
                type="text"
                value={newKeyLabel}
                onChange={(e) => setNewKeyLabel(e.target.value)}
                placeholder="Ex: Minha Chave 1"
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none text-sm"
              />
          </div>
          <div className="flex-[2]">
              <label className="text-xs text-slate-400 mb-1 block">Chave API</label>
              <input
                type="text"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder="Cole a Chave API Gemini (AI Studio)"
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none font-mono text-sm"
              />
          </div>
          <div className="w-24">
              <label className="text-xs text-slate-400 mb-1 block">Limite Diário</label>
              <input
                type="number"
                value={newKeyLimit}
                onChange={(e) => setNewKeyLimit(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none text-sm"
              />
          </div>
          <button
            onClick={addKey}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded flex items-center gap-2 transition-colors font-medium justify-center h-[38px]"
          >
            <Plus className="w-4 h-4" /> Adicionar
          </button>
        </div>

        <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
          {apiKeys.length === 0 && (
            <div className="text-center py-8 text-slate-500 border border-dashed border-slate-700 rounded bg-slate-900/50">
              Nenhuma chave API adicionada. A automação não pode iniciar sem pelo menos uma chave ativa.
            </div>
          )}
          {apiKeys.map((k, idx) => {
             const isSystemKey = k.key === process.env.API_KEY;
             const usagePercent = Math.min(100, Math.round(((k.usageCount || 0) / (k.usageLimit || 100)) * 100));
             const isNearLimit = usagePercent > 90;
             
             return (
                <div
                key={idx}
                className={`flex flex-col p-4 rounded-lg border transition-colors ${
                    !k.isActive 
                        ? 'bg-slate-900 border-slate-800 opacity-60' 
                        : k.isRateLimited
                            ? 'bg-red-950/20 border-red-500/30'
                            : k.errorCount > 0 
                                ? 'bg-orange-950/20 border-orange-500/30'
                                : isSystemKey 
                                    ? 'bg-purple-900/10 border-purple-500/30' 
                                    : 'bg-slate-800 border-slate-700'
                }`}
                >
                <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-4 overflow-hidden">
                        {/* Power Toggle */}
                        <button 
                            onClick={() => toggleActive(k.key)}
                            className={`p-2 rounded-full transition-all ${k.isActive ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' : 'bg-slate-700 text-slate-500 hover:bg-slate-600'}`}
                            title={k.isActive ? "Desativar Chave" : "Ativar Chave"}
                        >
                            <Power className="w-4 h-4" />
                        </button>

                        <div className="flex flex-col gap-1">
                            <div className="flex flex-col">
                                <span className="font-bold text-sm text-white flex items-center gap-2">
                                    {k.label || (isSystemKey ? "Chave de Sistema" : "Sem Apelido")}
                                    {isSystemKey && <ShieldCheck className="w-3 h-3 text-purple-400" />}
                                    {k.isRateLimited && <span className="text-[10px] bg-red-500 text-white px-1 rounded">RATE LIMITED</span>}
                                </span>
                                <span className="font-mono text-xs text-slate-500 truncate w-64 block" title={k.key}>
                                    {k.key.substring(0, 8)}...{k.key.substring(k.key.length - 6)}
                                </span>
                            </div>
                        </div>
                    </div>

                        <div className="flex items-center gap-2">
                            {/* Test Key Button */}
                            <button 
                                onClick={() => testKey(k.key)}
                                disabled={!!testingKey}
                                className={`text-[10px] px-2 py-1 rounded flex items-center gap-1 transition-colors border ${
                                    testingKey === k.key 
                                    ? 'bg-blue-900/50 border-blue-500 text-blue-200 cursor-wait' 
                                    : keyTestResults[k.key] === 'success'
                                        ? 'bg-green-900/30 border-green-500 text-green-400'
                                        : keyTestResults[k.key] === 'failure'
                                            ? 'bg-red-900/30 border-red-500 text-red-400'
                                            : 'bg-blue-900/30 hover:bg-blue-800 text-blue-300 border-blue-500/30'
                                }`}
                                title="Testar se a chave está funcionando"
                            >
                                {testingKey === k.key ? <Loader2 className="w-3 h-3 animate-spin" /> : 
                                 keyTestResults[k.key] === 'success' ? <Check className="w-3 h-3" /> :
                                 keyTestResults[k.key] === 'failure' ? <X className="w-3 h-3" /> :
                                 <ShieldCheck className="w-3 h-3" />}
                                
                                {testingKey === k.key ? "Testando..." : 
                                 keyTestResults[k.key] === 'success' ? "OK" :
                                 keyTestResults[k.key] === 'failure' ? "Erro" :
                                 "Testar"}
                            </button>

                            {/* Reset Usage Button */}
                            <button 
                                onClick={() => resetUsage(k.key)}
                                className="text-[10px] bg-slate-700 hover:bg-slate-600 text-slate-300 px-2 py-1 rounded flex items-center gap-1 transition-colors"
                                title="Resetar uso diário manualmente"
                            >
                                <RefreshCw className="w-3 h-3" /> Resetar Uso
                            </button>
                        
                        {!isSystemKey && (
                            <button
                                onClick={() => removeKey(k.key)}
                                className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                title="Excluir Chave"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Usage Bar */}
                <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden relative">
                    <div 
                        className={`h-full transition-all duration-500 ${
                            k.isRateLimited ? 'bg-red-500 animate-pulse' :
                            isNearLimit ? 'bg-orange-500' : 
                            'bg-green-500'
                        }`} 
                        style={{ width: `${usagePercent}%` }}
                    />
                </div>
                <div className="flex justify-between text-[10px] text-slate-400 mt-1 font-mono">
                    <span>Uso: {k.usageCount || 0} / {k.usageLimit || 100} reqs</span>
                    <span>{usagePercent}%</span>
                </div>
                
                </div>
             );
          })}
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;