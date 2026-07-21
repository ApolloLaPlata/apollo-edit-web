import React, { useState, useEffect, useRef } from 'react';
import { ApiKey, Character, GeneratedImage, GenerationSettings, Project } from '../types';
import { DEFAULT_SETTINGS, PROJECT_COLORS } from '../constants';
import CharacterManager from '../components/CharacterManager';
import JobRunner from '../components/JobRunner';
import SettingsPanel, { getIconComponent } from '../components/SettingsPanel';
import Gallery from '../components/Gallery';
import CharacterCreator from '../components/CharacterCreator';
import ImageStudio from '../components/ImageStudio';
import ScriptRoom from '../components/ScriptRoom';
import ThumbnailStudio from '../components/ThumbnailStudio';
import SocialPosts from '../components/SocialPosts';
import CarouselCreator from '../components/CarouselCreator';
import ErrorBoundary from '../components/ErrorBoundary';
import Lightbox from '../components/Lightbox';
import VideoDirector from '../components/VideoDirector';
import { Toaster } from 'react-hot-toast';
import { Users, PlaySquare, Image as ImageIcon, Settings, Database, Wand2, Palette, BookOpen, MonitorPlay, MessageSquare, Layers, Film, LogOut } from 'lucide-react';
import { db } from '../utils/db';
import { generateImage } from '../services/imageGenerator';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import { supabase } from '../lib/supabaseClient';
import toast from 'react-hot-toast';

const Dashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roster' | 'creator' | 'studio' | 'videodirector' | 'thumbnail' | 'social' | 'carousel' | 'script' | 'jobs' | 'gallery' | 'settings'>('jobs');

  const [isDbLoading, setIsDbLoading] = useState(true);
  const [lightboxImageIndex, setLightboxImageIndex] = useState<number | null>(null);

  const [projects, setProjects] = useState<Project[]>(() => {
    try {
      const saved = localStorage.getItem('gemini_projects');
      return saved ? JSON.parse(saved) : [{ id: 'default', name: 'Canal Principal' }];
    } catch {
      return [{ id: 'default', name: 'Canal Principal' }];
    }
  });
  const [activeProjectId, setActiveProjectId] = useState<string>(() => {
    return localStorage.getItem('gemini_active_project') || 'default';
  });

  useEffect(() => {
    try {
      localStorage.setItem('gemini_projects', JSON.stringify(projects));
    } catch (e) {
      console.error("Failed to save projects to localStorage", e);
    }
  }, [projects]);

  useEffect(() => {
    try {
      localStorage.setItem('gemini_active_project', activeProjectId);
    } catch (e) {
      console.error("Failed to save active project to localStorage", e);
    }
  }, [activeProjectId]);

  // Settings and API Keys are light, so we keep them in LocalStorage for speed
  const [apiKeys, setApiKeys] = useState<ApiKey[]>(() => {
    try {
        const saved = localStorage.getItem('gemini_api_keys');
        const keys: ApiKey[] = saved ? JSON.parse(saved) : [];
        
        // AUTO-DETECT CURRENT ACCOUNT KEY logic
        // We filter out any old "System Keys" to ensure we always use the one from the CURRENT env
        // This allows the user to clone the repo to a different account and immediately use that account's quota
        const manualKeys = keys.filter(k => k.key !== process.env.API_KEY && k.label !== 'Chave de Sistema (Conta Atual)');
        
        if (process.env.API_KEY) {
            const systemKey: ApiKey = {
                key: process.env.API_KEY,
                label: 'Chave de Sistema (Conta Atual)',
                isActive: true,
                errorCount: 0,
                usageCount: 0,
                usageLimit: 100, // Default limit
                lastReset: Date.now(),
                isRateLimited: false
            };
            // System key always goes first
            return [systemKey, ...manualKeys];
        }
        
        return manualKeys;
    } catch { 
        // Fallback if LS fails
        if (process.env.API_KEY) {
            return [{
                key: process.env.API_KEY,
                label: 'Chave de Sistema (Conta Atual)',
                isActive: true,
                errorCount: 0,
                usageCount: 0,
                usageLimit: 100,
                lastReset: Date.now(),
                isRateLimited: false
            }];
        }
        return []; 
    }
  });

  const apiKeysRef = useRef(apiKeys);
  useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  // Check for daily resets on load and periodically
  useEffect(() => {
      // Import dynamically to avoid circular dependency issues if any (though utils are safe)
      import('../utils/apiKeyRotation').then(({ checkDailyReset }) => {
          setApiKeys(prev => checkDailyReset(prev));
      });
      
      // Optional: Check every minute
      const interval = setInterval(() => {
          import('../utils/apiKeyRotation').then(({ checkDailyReset }) => {
              setApiKeys(prev => checkDailyReset(prev));
          });
      }, 60000);
      
      return () => clearInterval(interval);
  }, []);

  const [settings, setSettings] = useState<GenerationSettings>(() => {
    try {
        const saved = localStorage.getItem('gemini_settings');
        // Merge saved settings with defaults to ensure new fields (like useStoryContinuity) exist
        return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch { return DEFAULT_SETTINGS; }
  });

  // Characters and Gallery are heavy, so we load them from IndexedDB
  const [characters, setCharacters] = useState<Character[]>([]);
  // Use a ref to track characters for async operations (prevents stale closures during rapid deletes)
  const charactersRef = useRef<Character[]>([]);

  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);

  const activeProject = projects.find(p => p.id === activeProjectId) || projects[0];
  const activePreset = activeProject?.presets?.find(p => p.id === activeProject.activePresetId);

  const effectiveSettings: GenerationSettings = {
    ...settings,
    globalContext: activePreset?.globalContext ?? activeProject?.globalContext ?? (activeProject?.id === 'default' ? settings.globalContext : ''),
    negativePrompt: activePreset?.negativePrompt ?? activeProject?.negativePrompt ?? (activeProject?.id === 'default' ? settings.negativePrompt : ''),
    sceneContext: activePreset?.sceneContext ?? activeProject?.sceneContext ?? (activeProject?.id === 'default' ? settings.sceneContext : ''),
    styleReferenceImage: activePreset?.styleReferenceImage ?? activeProject?.styleReferenceImage ?? (activeProject?.id === 'default' ? settings.styleReferenceImage : undefined),
    aspectRatio: activeProject?.aspectRatio ?? (activeProject?.id === 'default' ? settings.aspectRatio : '16:9'),
    modelId: activeProject?.modelId ?? (activeProject?.id === 'default' ? settings.modelId : 'gemini-3.1-flash-image-preview'),
    imageSize: activeProject?.imageSize ?? (activeProject?.id === 'default' ? settings.imageSize : '1K'),
    brandKit: activeProject?.brandKit ?? (activeProject?.id === 'default' ? settings.brandKit : { colors: [] }),
    knowledgeBase: activeProject?.knowledgeBase ?? (activeProject?.id === 'default' ? settings.knowledgeBase : []),
  };

  // Inject ComfyUI workflow JSONs based on active project
  if (activeProject?.defaultImageWorkflowId && settings.comfyWorkflows) {
      const wf = settings.comfyWorkflows.find(w => w.id === activeProject.defaultImageWorkflowId);
      if (wf) {
          effectiveSettings.comfyImageWorkflow = wf.json;
      }
  }
  if (activeProject?.defaultVideoWorkflowId && settings.comfyWorkflows) {
      const wf = settings.comfyWorkflows.find(w => w.id === activeProject.defaultVideoWorkflowId);
      if (wf) {
          effectiveSettings.comfyVideoWorkflow = wf.json;
      }
  }

  const updateSetting = (field: keyof GenerationSettings, value: any) => {
    if (['globalContext', 'negativePrompt', 'sceneContext', 'styleReferenceImage'].includes(field)) {
        setProjects(prev => prev.map(p => {
            if (p.id === activeProjectId) {
                if (p.activePresetId && p.presets) {
                    // Update the active preset
                    return {
                        ...p,
                        presets: p.presets.map(preset => 
                            preset.id === p.activePresetId ? { ...preset, [field]: value } : preset
                        )
                    };
                } else {
                    // Update the project directly
                    return { ...p, [field]: value };
                }
            }
            return p;
        }));
    } else if (['aspectRatio', 'modelId', 'imageSize', 'brandKit', 'knowledgeBase'].includes(field)) {
        setProjects(prev => prev.map(p => 
            p.id === activeProjectId ? { ...p, [field]: value } : p
        ));
    } else {
        setSettings(prev => ({ ...prev, [field]: value }));
    }
  };

  const activeCharacters = characters.filter(c => (c.projectId || 'default') === activeProjectId);
  const activeImages = generatedImages.filter(img => (img.projectId || 'default') === activeProjectId);

  const openLightbox = (image: GeneratedImage) => {
    const index = activeImages.findIndex(img => img.id === image.id);
    if (index !== -1) {
      setLightboxImageIndex(index);
    }
  };

  const closeLightbox = () => setLightboxImageIndex(null);

  const handleNextImage = () => {
    if (lightboxImageIndex !== null && lightboxImageIndex < activeImages.length - 1) {
      setLightboxImageIndex(lightboxImageIndex + 1);
    }
  };

  const handlePrevImage = () => {
    if (lightboxImageIndex !== null && lightboxImageIndex > 0) {
      setLightboxImageIndex(lightboxImageIndex - 1);
    }
  };

  // Load Data on Mount
  useEffect(() => {
    const loadData = async () => {
        try {
            const rawChars = await db.characters.getAll();
            
            // MIGRATION: Handle legacy characters that only had `imageData` (single string)
            const migratedChars: Character[] = rawChars.map((c: any) => {
                if (c.imageData && !c.images) {
                    return {
                        ...c,
                        images: [c.imageData], // Move single image to array
                        previewUrl: c.imageData
                    };
                }
                return c;
            });

            const loadedImages = await db.gallery.getAll();
            setCharacters(migratedChars);
            charactersRef.current = migratedChars;
            setGeneratedImages(loadedImages || []);
        } catch (error) {
            console.error("Falha ao carregar dados do DB:", error);
        } finally {
            setIsDbLoading(false);
        }
    };
    loadData();
  }, []);

  // Save Settings/Keys to LocalStorage
  useEffect(() => {
      try {
          localStorage.setItem('gemini_api_keys', JSON.stringify(apiKeys));
      } catch (e) {
          console.error("Failed to save api keys to localStorage", e);
      }
  }, [apiKeys]);
  useEffect(() => {
      try {
          localStorage.setItem('gemini_settings', JSON.stringify(settings));
      } catch (e) {
          console.error("Failed to save settings to localStorage", e);
      }
  }, [settings]);

  // Auto-heal: Clear any legacy 24-hour blocks from old code
  useEffect(() => {
      setApiKeys(prev => {
          let changed = false;
          const now = Date.now();
          const newKeys = prev.map(k => {
              // If rateLimitedUntil is more than 5 minutes in the future, it's a legacy 24h block
              if (k.isRateLimited && k.rateLimitedUntil && (k.rateLimitedUntil - now > 5 * 60 * 1000)) {
                  changed = true;
                  return { ...k, isRateLimited: false, rateLimitedUntil: 0 };
              }
              return k;
          });
          return changed ? newKeys : prev;
      });
  }, []);

  // --- CHARACTER MANAGEMENT HANDLERS ---
  
  // 1. ADD
  const handleAddCharacter = async (newChar: Character) => {
      const charWithProject = { ...newChar, projectId: newChar.projectId || activeProjectId };
      // Optimistic UI Update
      setCharacters(prev => {
          const next = [...prev, charWithProject];
          charactersRef.current = next;
          return next;
      });
      // DB Sync
      try {
          await db.characters.save(charWithProject);
      } catch (err) {
          console.error("Failed to save character:", err);
      }
  };

  // 2. UPDATE
  const handleUpdateCharacter = async (updatedChar: Character) => {
      // Optimistic UI Update
      setCharacters(prev => {
          const next = prev.map(c => c.id === updatedChar.id ? updatedChar : c);
          charactersRef.current = next;
          return next;
      });
      // DB Sync
      try {
          await db.characters.save(updatedChar);
      } catch (err) {
          console.error("Failed to update character:", err);
      }
  };

  // 3. DELETE
  const handleDeleteCharacter = async (id: string) => {
      // Optimistic UI Update
      setCharacters(prev => {
          const next = prev.filter(c => c.id !== id);
          charactersRef.current = next;
          return next;
      });
      // DB Sync
      try {
          await db.characters.delete(id);
      } catch (err) {
          console.error("Failed to delete character:", err);
      }
  };

  // Optimized adder for gallery to avoid re-saving everything
  const addGeneratedImage = async (img: GeneratedImage) => {
    const imgWithProject = { ...img, projectId: img.projectId || activeProjectId };
    setGeneratedImages((prev) => [...prev, imgWithProject]);
    await db.gallery.save(imgWithProject);
  };

  const updateGeneratedImage = async (id: string, updates: Partial<GeneratedImage>) => {
      // Optimistic Update
      setGeneratedImages((prev) => {
          const newImages = prev.map(img => img.id === id ? { ...img, ...updates } : img);
          
          // Background DB Sync using the latest state directly
          const target = newImages.find(img => img.id === id);
          if (target) {
              db.gallery.save(target).catch(err => console.error("Gallery save failed", err));
          }
          
          return newImages;
      });
  };

  const removeGeneratedImage = (id: string) => {
      // Optimistic Update
      setGeneratedImages((prev) => prev.filter(img => img.id !== id));
      // Background DB Sync
      db.gallery.delete(id).catch(err => console.error("Gallery delete failed", err));
  };

  const clearGallery = async () => {
      const imagesToDelete = generatedImages.filter(img => (img.projectId || 'default') === activeProjectId);
      setGeneratedImages(prev => prev.filter(img => (img.projectId || 'default') !== activeProjectId));
      
      // Delete them one by one from DB
      for (const img of imagesToDelete) {
          await db.gallery.delete(img.id);
      }
  };

  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerateImage = async (img: GeneratedImage) => {
      setIsRegenerating(true);
      try {
          const newImageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => {
                  return await generateImage(
                      apiKey,
                      img.prompt,
                      charactersRef.current.filter(c => (c.projectId || 'default') === activeProjectId),
                      effectiveSettings
                  );
              }
          );

          await updateGeneratedImage(img.id, {
              imageUrl: newImageUrl,
          });
          toast.success("Imagem regenerada com sucesso!");
      } catch (e: any) {
          toast.error("Falha ao regenerar: " + e.message);
      } finally {
          setIsRegenerating(false);
      }
  };

  if (isDbLoading) {
      return (
          <div className="h-screen w-screen bg-slate-950 flex items-center justify-center text-slate-400 flex-col gap-4">
              <Database className="w-12 h-12 animate-pulse text-purple-500" />
              <p>Inicializando Armazenamento Seguro...</p>
          </div>
      );
  }

  return (
    <div className="flex h-screen bg-black text-slate-100 font-sans overflow-hidden selection:bg-purple-500 selection:text-white">
      {/* Sidebar Navigation */}
      <div className="w-20 lg:w-64 flex-shrink-0 bg-slate-900/50 backdrop-blur-md border-r border-slate-800 flex flex-col">
        <div className="p-4 lg:p-6 flex items-center gap-3 border-b border-slate-800">
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-lg ${PROJECT_COLORS.find(c => c.id === (activeProject?.color || 'blue'))?.class || 'bg-blue-500'}`}>
                {getIconComponent(activeProject?.icon, "w-5 h-5 text-white")}
            </div>
            <h1 className="text-xl font-bold hidden lg:block tracking-tight text-white">Gemini<span className="text-purple-500">Studio</span></h1>
        </div>

        {/* Project Selector */}
        <div className="p-4 border-b border-slate-800 hidden lg:block">
            <label className="text-xs text-slate-500 uppercase font-bold mb-2 block">Projeto / Canal</label>
            <select 
                value={activeProjectId} 
                onChange={(e) => setActiveProjectId(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm text-white focus:ring-2 focus:ring-purple-500"
            >
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
            <button
                onClick={() => setActiveTab('jobs')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'jobs' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <PlaySquare className={`w-5 h-5 ${activeTab === 'jobs' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Auto Execução</span>
            </button>
            
            <button
                onClick={() => setActiveTab('creator')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'creator' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Wand2 className={`w-5 h-5 ${activeTab === 'creator' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Laboratório</span>
            </button>

            <button
                onClick={() => setActiveTab('studio')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'studio' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Palette className={`w-5 h-5 ${activeTab === 'studio' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Estúdio</span>
            </button>

            <button
                onClick={() => setActiveTab('thumbnail')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'thumbnail' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <MonitorPlay className={`w-5 h-5 ${activeTab === 'thumbnail' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Thumbnails</span>
            </button>

            <button
                onClick={() => setActiveTab('social')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'social' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <MessageSquare className={`w-5 h-5 ${activeTab === 'social' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Postagens</span>
            </button>

            <button
                onClick={() => setActiveTab('carousel')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'carousel' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Layers className={`w-5 h-5 ${activeTab === 'carousel' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Carrossel</span>
            </button>
            
            <button
                onClick={() => setActiveTab('script')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'script' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <BookOpen className={`w-5 h-5 ${activeTab === 'script' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Sala de Roteiro</span>
            </button>

            <button
                onClick={() => setActiveTab('videodirector')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'videodirector' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Film className={`w-5 h-5 ${activeTab === 'videodirector' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Diretor de Vídeo</span>
            </button>

            <button
                onClick={() => setActiveTab('roster')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'roster' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Users className={`w-5 h-5 ${activeTab === 'roster' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Personagens</span>
            </button>
            <button
                onClick={() => setActiveTab('gallery')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'gallery' ? 'bg-purple-600 text-white shadow-lg shadow-purple-900/50 border-purple-500' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <ImageIcon className={`w-5 h-5 ${activeTab === 'gallery' ? 'text-white' : 'text-orange-400'}`} />
                <span className="hidden lg:block font-medium">Galeria</span>
            </button>
        </nav>

        <div className="p-4 border-t border-slate-800">
             <button
                onClick={() => setActiveTab('settings')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all border border-transparent ${activeTab === 'settings' ? 'bg-slate-800 text-white border-slate-600' : 'text-slate-400 hover:bg-slate-800 hover:text-white hover:border-slate-700'}`}
            >
                <Settings className="w-5 h-5" />
                <span className="hidden lg:block font-medium">Configurações</span>
            </button>
            <button
                onClick={async () => {
                  await supabase.auth.signOut();
                }}
                className="w-full flex items-center gap-3 px-4 py-3 mt-2 rounded-lg transition-all border border-transparent text-red-400 hover:bg-red-900/30 hover:text-red-300"
            >
                <LogOut className="w-5 h-5" />
                <span className="hidden lg:block font-medium">Sair</span>
            </button>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="flex-1 p-4 lg:p-6 overflow-hidden relative bg-black flex flex-col">
        {/* Background Gradients - Purple & Orange */}
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none z-0">
             <div className="absolute top-[-10%] right-[-5%] w-96 h-96 bg-purple-600/10 rounded-full blur-3xl"></div>
             <div className="absolute bottom-[-10%] left-[-5%] w-96 h-96 bg-orange-600/10 rounded-full blur-3xl"></div>
             <div className="absolute top-[40%] left-[30%] w-64 h-64 bg-indigo-900/10 rounded-full blur-3xl"></div>
        </div>

        <div className="relative z-10 flex-1 overflow-hidden">
            {activeTab === 'roster' && (
                <CharacterManager 
                    characters={activeCharacters} 
                    onAddCharacter={handleAddCharacter}
                    onUpdateCharacter={handleUpdateCharacter}
                    onDeleteCharacter={handleDeleteCharacter}
                    apiKeys={apiKeys}
                    setApiKeys={setApiKeys}
                />
            )}
            {activeTab === 'creator' && (
                <CharacterCreator 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    onSaveCharacter={handleAddCharacter}
                    addGeneratedImage={addGeneratedImage}
                    settings={effectiveSettings}
                />
            )}
            {activeTab === 'studio' && (
                <ImageStudio 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    addGeneratedImage={addGeneratedImage}
                    characters={characters}
                    settings={effectiveSettings}
                    onImageClick={openLightbox}
                />
            )}
            {activeTab === 'thumbnail' && (
                <ThumbnailStudio 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    addGeneratedImage={addGeneratedImage}
                    characters={activeCharacters}
                    settings={effectiveSettings}
                    onImageClick={openLightbox}
                />
            )}
            {activeTab === 'social' && (
                <SocialPosts 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    addGeneratedImage={addGeneratedImage}
                    characters={activeCharacters}
                    settings={effectiveSettings}
                    onImageClick={openLightbox}
                />
            )}
            {activeTab === 'carousel' && (
                <CarouselCreator 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    addGeneratedImage={addGeneratedImage}
                    characters={activeCharacters}
                    settings={effectiveSettings}
                    onImageClick={openLightbox}
                />
            )}
            {activeTab === 'script' && (
                <ScriptRoom 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    characters={activeCharacters}
                    globalContext={effectiveSettings.globalContext}
                    settings={effectiveSettings}
                />
            )}
            {activeTab === 'videodirector' && (
                <VideoDirector 
                    settings={effectiveSettings}
                />
            )}
            {activeTab === 'jobs' && (
                <JobRunner 
                    apiKeys={apiKeys}
                    setApiKeys={setApiKeys}
                    characters={activeCharacters} 
                    settings={effectiveSettings}
                    onUpdateSetting={updateSetting}
                    addGeneratedImage={addGeneratedImage}
                    updateGeneratedImage={updateGeneratedImage}
                    onNavigateToSettings={() => setActiveTab('settings')}
                    generatedImages={activeImages}
                    onImageClick={openLightbox}
                />
            )}
            {activeTab === 'gallery' && (
                <ErrorBoundary>
                    <Gallery 
                        images={activeImages} 
                        onClearGallery={clearGallery} 
                        apiKeys={apiKeys}
                        setApiKeys={setApiKeys}
                        settings={effectiveSettings}
                        characters={activeCharacters}
                        addGeneratedImage={addGeneratedImage}
                        updateGeneratedImage={updateGeneratedImage}
                        onRemoveImage={removeGeneratedImage}
                        onImageClick={openLightbox}
                    />
                </ErrorBoundary>
            )}
            {activeTab === 'settings' && (
                <SettingsPanel 
                    apiKeys={apiKeys} 
                    setApiKeys={setApiKeys}
                    settings={effectiveSettings}
                    setSettings={setSettings}
                    onUpdateSetting={updateSetting}
                    projects={projects}
                    setProjects={setProjects}
                    activeProjectId={activeProjectId}
                    setActiveProjectId={setActiveProjectId}
                />
            )}
        </div>
      </main>

      <Lightbox 
        isOpen={lightboxImageIndex !== null}
        onClose={closeLightbox}
        image={lightboxImageIndex !== null ? activeImages[lightboxImageIndex] : null}
        onNext={handleNextImage}
        onPrev={handlePrevImage}
        hasNext={lightboxImageIndex !== null && lightboxImageIndex < activeImages.length - 1}
        hasPrev={lightboxImageIndex !== null && lightboxImageIndex > 0}
        onRegenerate={handleRegenerateImage}
        isRegenerating={isRegenerating}
      />
      
      <Toaster 
        position="bottom-right"
        toastOptions={{
          style: {
            background: '#1e293b',
            color: '#fff',
            border: '1px solid #334155',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
};

export default Dashboard;