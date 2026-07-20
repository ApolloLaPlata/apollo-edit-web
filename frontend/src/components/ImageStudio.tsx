import React, { useState, useRef, useEffect } from 'react';
import { ApiKey, GeneratedImage, GenerationSettings, Character } from '../types';
import { editGeneratedImage, describeImage, enhancePrompt, analyzeImageForPrompt } from '../services/geminiService';
import { generateImage } from '../services/imageGenerator';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Wand2, Upload, Loader2, X, Zap, ScanEye, RefreshCw, Palette, Settings2, Download, Sparkles, ShieldAlert, History, Clock } from 'lucide-react';
import { MODELS, ASPECT_RATIOS, VISUAL_STYLES } from '../constants';

import CharacterSelector from './CharacterSelector';

interface ImageStudioProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  addGeneratedImage: (img: GeneratedImage) => void;
  characters: Character[];
  settings?: GenerationSettings;
  onImageClick?: (image: GeneratedImage) => void;
}

const ImageStudio: React.FC<ImageStudioProps> = ({ apiKeys, setApiKeys, addGeneratedImage, characters, settings, onImageClick }) => {
  const [prompt, setPrompt] = useState('');
  const [referenceImage, setReferenceImage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDescribing, setIsDescribing] = useState(false);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<GeneratedImage | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Settings specific to Studio
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');
  const [aspectRatio, setAspectRatio] = useState('16:9');
  const [imageSize, setImageSize] = useState<'1K' | '2K' | '4K'>('1K');
  const [batchSize, setBatchSize] = useState(1);
  const [selectedStyle, setSelectedStyle] = useState('none');
  const [globalContext, setGlobalContext] = useState('');
  const [negativePrompt, setNegativePrompt] = useState('');
  const [useGrounding, setUseGrounding] = useState(false);
  
  // Edit Mode State
  const [isEditing, setIsEditing] = useState(false);
  const [showEditInput, setShowEditInput] = useState(false);
  const [editInstruction, setEditInstruction] = useState('');
  
  // Prompt History State
  const [promptHistory, setPromptHistory] = useState<string[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const apiKeysRef = useRef(apiKeys);
  React.useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  // Load History
  useEffect(() => {
      const saved = localStorage.getItem('gemini_prompt_history');
      if (saved) {
          try {
              setPromptHistory(JSON.parse(saved));
          } catch (e) {
              console.error("Failed to load prompt history", e);
          }
      }
  }, []);

  const savePromptToHistory = (newPrompt: string) => {
      if (!newPrompt.trim()) return;
      setPromptHistory(prev => {
          const filtered = prev.filter(p => p !== newPrompt); // Remove duplicates
          const updated = [newPrompt, ...filtered].slice(0, 20); // Keep last 20
          try {
              localStorage.setItem('gemini_prompt_history', JSON.stringify(updated));
          } catch (e) {
              console.error("Failed to save prompt history to localStorage", e);
          }
          return updated;
      });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setReferenceImage(ev.target?.result as string);
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  const insertCharacterTag = (tagName: string) => {
      if (!prompt.includes(tagName)) {
          setPrompt(prev => prev ? `${prev} ${tagName}` : tagName);
      }
  };

  const handleStyleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newStyle = e.target.value;
    setSelectedStyle(newStyle);
    
    if (newStyle === 'none') return;

    const styleDef = VISUAL_STYLES.find(s => s.id === newStyle);
    if (styleDef) {
        setGlobalContext(prev => {
            const cleanLabel = styleDef.label;
            if (!prev.trim()) return cleanLabel;
            // Prevent duplicate appending if it's already at the end
            if (prev.endsWith(cleanLabel)) return prev;
            return `${prev}, ${cleanLabel}`;
        });
    }
  };

  const handleEnhancePrompt = async () => {
      if (!prompt.trim()) return;
      
      setIsEnhancing(true);
      try {
          const enhanced = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await enhancePrompt(prompt, globalContext, settings || {} as GenerationSettings, apiKey)
          );
          
          setPrompt(enhanced);
      } catch (e: any) {
          console.error(e);
          toast.error("Falha ao melhorar prompt: " + e.message);
      } finally {
          setIsEnhancing(false);
      }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setGeneratedResult(null);
    setError(null);
    setShowEditInput(false);
    
    // Save to history
    savePromptToHistory(prompt);

    try {
        // Loop for Batch Size
        for (let i = 0; i < batchSize; i++) {
            let imageUrl = "";

            const tempSettings: any = {
                ...settings,
                modelId: selectedModel,
                aspectRatio: aspectRatio,
                imageSize: imageSize,
                globalContext: globalContext,
                negativePrompt: negativePrompt,
                useGrounding: useGrounding,
                sceneContext: "",
            };

            // Use the unified image generator
            imageUrl = await executeWithKeyRotation(
                apiKeysRef,
                setApiKeys,
                async (apiKey) => await generateImage(
                    apiKey, 
                    prompt, 
                    characters, 
                    tempSettings,
                    referenceImage || undefined
                )
            );

            // Only set result for the first one to show immediately, others go to gallery
            const galleryItem: GeneratedImage = {
                id: crypto.randomUUID(),
                prompt: `[Estúdio] ${prompt}`,
                imageUrl: imageUrl,
                timestamp: Date.now(),
                characterIds: [],
                aspectRatio: aspectRatio
            };
            
            if (i === 0) setGeneratedResult(galleryItem);

            // Save to gallery
            addGeneratedImage(galleryItem);
            
            // Small delay between batch requests
            if (i < batchSize - 1) await new Promise(r => setTimeout(r, 1000));
        }

    } catch (error: any) {
        console.error(error);
        let msg = error.message || "Erro desconhecido";
        if (msg.includes('429') || msg.includes('quota')) {
            msg = "Cota da API excedida (Erro 429).";
        }
        setError(msg);
    } finally {
        setIsGenerating(false);
    }
  };

  const handleEdit = async () => {
      if (!generatedResult || !editInstruction.trim()) return;
      
      setIsEditing(true);

      const tempSettings: any = {
          modelId: selectedModel,
          aspectRatio: aspectRatio,
      };

      try {
          const newImageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await editGeneratedImage(apiKey, generatedResult.imageUrl, editInstruction, tempSettings)
          );
          
          const galleryItem: GeneratedImage = {
            id: crypto.randomUUID(),
            prompt: `[Edição Estúdio: ${editInstruction}] ${prompt}`,
            imageUrl: newImageUrl,
            timestamp: Date.now(),
            characterIds: [],
            aspectRatio: aspectRatio
        };
        
        setGeneratedResult(galleryItem);
        addGeneratedImage(galleryItem);
        setShowEditInput(false);
        setEditInstruction('');

      } catch (error: any) {
          toast.error("Edição falhou: " + error.message);
      } finally {
          setIsEditing(false);
      }
  };

  const handleDescribeImage = async () => {
      // Use reference image or generated result
      const targetImage = generatedResult?.imageUrl || referenceImage;
      if (!targetImage) return;

      setIsDescribing(true);
      try {
          const description = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await describeImage(apiKey, targetImage)
          );
          setPrompt(description); // Replace prompt with description
      } catch (e: any) {
          toast.error("Falha ao descrever imagem: " + e.message);
      } finally {
          setIsDescribing(false);
      }
  };

  const handleAnalyzeImage = async () => {
      const targetImage = referenceImage;
      if (!targetImage) return;

      setIsAnalyzing(true);
      try {
          const stylePrompt = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await analyzeImageForPrompt(apiKey, targetImage)
          );
          setPrompt(stylePrompt);
          toast.success("Estilo analisado com sucesso!");
      } catch (e: any) {
          toast.error("Falha ao analisar estilo: " + e.message);
      } finally {
          setIsAnalyzing(false);
      }
  };

  const handleAnalyzeGeneratedImage = async () => {
      const targetImage = generatedResult?.imageUrl;
      if (!targetImage) return;

      setIsAnalyzing(true);
      try {
          const stylePrompt = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await analyzeImageForPrompt(apiKey, targetImage)
          );
          setPrompt(stylePrompt);
          toast.success("Estilo analisado com sucesso!");
      } catch (e: any) {
          toast.error("Falha ao analisar estilo: " + e.message);
      } finally {
          setIsAnalyzing(false);
      }
  };

  const handleDownload = () => {
    if (generatedResult) {
        const link = document.createElement('a');
        link.href = generatedResult.imageUrl;
        link.download = `studio_image_${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
  };

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 p-2">
      {/* Left Panel: Inputs */}
      <div className="w-full md:w-1/3 bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-6 overflow-y-auto">
        <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
                <Palette className="w-6 h-6 text-purple-400" />
                Estúdio de Imagem
            </h2>
            <p className="text-sm text-slate-400">
                Crie arte conceitual, paisagens e cenas com estilos visuais específicos.
            </p>
        </div>

        {/* Configuration Grid */}
        <div className="grid grid-cols-1 gap-4">
            {/* Model */}
            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                    <Zap className="w-3 h-3 text-yellow-500" /> Modelo
                </label>
                <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                >
                {MODELS.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                ))}
                </select>
            </div>

            {/* Styles & Ratio Row */}
            <div className="flex gap-2">
                <div className="flex-1 bg-slate-800 p-3 rounded-lg border border-slate-700">
                    <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                        <Palette className="w-3 h-3 text-purple-400" /> Estilo Predefinido
                    </label>
                    <select
                    value={selectedStyle}
                    onChange={handleStyleChange}
                    className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                    >
                    {VISUAL_STYLES.map((s) => (
                        <option key={s.id} value={s.id}>{s.label}</option>
                    ))}
                    </select>
                </div>

                <div className="flex-1 bg-slate-800 p-3 rounded-lg border border-slate-700">
                    <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                        <Settings2 className="w-3 h-3 text-blue-400" /> Proporção
                    </label>
                    <select
                    value={aspectRatio}
                    onChange={(e) => setAspectRatio(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                    >
                    {ASPECT_RATIOS.map((r) => (
                        <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                    </select>
                </div>
            </div>

            {/* Resolution Selector (New) */}
            {selectedModel.includes('gemini-3.1') && (
                 <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                    <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                        <Settings2 className="w-3 h-3 text-green-400" /> Resolução (Nano Banana 2)
                    </label>
                    <div className="flex gap-2">
                        {['1K', '2K', '4K'].map((res) => (
                            <button
                                key={res}
                                onClick={() => setImageSize(res as any)}
                                className={`flex-1 py-1 text-xs font-bold rounded border ${
                                    imageSize === res ? 'bg-green-600 text-white border-green-500' : 'bg-slate-900 text-slate-400 border-slate-600 hover:bg-slate-800'
                                }`}
                            >
                                {res}
                            </button>
                        ))}
                    </div>
                 </div>
            )}

            {/* Global Context Input */}
            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                 <label className="text-xs font-bold text-slate-400 uppercase mb-2 block">
                     Direção de Arte / Contexto Global
                 </label>
                 <textarea 
                    value={globalContext}
                    onChange={(e) => setGlobalContext(e.target.value)}
                    placeholder="Ex: Cyberpunk, Luzes neon, Iluminação cinematográfica, Pintura a óleo..."
                    className="w-full h-16 bg-slate-900 border border-slate-600 rounded p-2 text-white text-xs resize-none focus:ring-2 focus:ring-purple-500 outline-none"
                 />
            </div>

            {/* Negative Prompt */}
            <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                 <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                     <ShieldAlert className="w-3 h-3 text-red-400" /> Prompt Negativo Global
                 </label>
                 <textarea 
                    value={negativePrompt}
                    onChange={(e) => setNegativePrompt(e.target.value)}
                    placeholder="Evitar texto, baixa qualidade, marca d'água..."
                    className="w-full h-12 bg-slate-900 border border-slate-600 rounded p-2 text-white text-xs resize-none focus:ring-2 focus:ring-red-500 outline-none placeholder-slate-600"
                 />
            </div>

            {/* Grounding Toggle */}
            <div className="flex gap-2">
                <div 
                    onClick={() => setUseGrounding(!useGrounding)}
                    className={`flex-1 p-3 rounded-lg border cursor-pointer transition-all flex items-center gap-3 ${useGrounding ? 'bg-blue-900/20 border-blue-500' : 'bg-slate-800 border-slate-700 hover:bg-slate-750'}`}
                >
                    <div className={`w-4 h-4 rounded border flex items-center justify-center ${useGrounding ? 'bg-blue-500 border-blue-400' : 'border-slate-500'}`}>
                        {useGrounding && <Zap className="w-3 h-3 text-white fill-current" />}
                    </div>
                    <div>
                        <span className={`text-xs font-bold block ${useGrounding ? 'text-blue-300' : 'text-slate-400'}`}>Grounding</span>
                    </div>
                </div>

                {/* Batch Size Selector */}
                <div className="bg-slate-800 p-2 rounded-lg border border-slate-700 flex items-center gap-2">
                    <label className="text-xs font-bold text-slate-400 uppercase whitespace-nowrap pl-1">
                        Qtd:
                    </label>
                    <select
                        value={batchSize}
                        onChange={(e) => setBatchSize(Number(e.target.value))}
                        className="bg-slate-900 border border-slate-600 rounded px-2 py-1 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none"
                    >
                        <option value={1}>1</option>
                        <option value={2}>2</option>
                        <option value={3}>3</option>
                        <option value={4}>4</option>
                    </select>
                </div>
            </div>
        </div>

        {/* Characters */}
        <CharacterSelector 
            characters={characters}
            onSelect={(char) => insertCharacterTag(char.name)}
            mode="insert"
            selectedIds={characters.filter(c => prompt.includes(c.name)).map(c => c.id)}
        />

        {/* Reference Image */}
        <div className="space-y-2">
            <div className="flex justify-between items-end">
                <label className="text-sm font-medium text-slate-300">Imagem de Referência (Opcional)</label>
                <div className="flex gap-2">
                    {(referenceImage && !isDescribing) && (
                        <button 
                            onClick={handleDescribeImage}
                            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 bg-blue-900/30 px-2 py-1 rounded"
                            title="Descrever o que tem na imagem"
                        >
                            {isDescribing ? <Loader2 className="w-3 h-3 animate-spin" /> : <ScanEye className="w-3 h-3" />} Descrever
                        </button>
                    )}
                    {(referenceImage && !isAnalyzing) && (
                        <button 
                            onClick={handleAnalyzeImage}
                            className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 bg-purple-900/30 px-2 py-1 rounded"
                            title="Extrair um prompt de estilo detalhado desta imagem"
                        >
                            {isAnalyzing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />} Analisar Estilo
                        </button>
                    )}
                </div>
            </div>
            
            <div 
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-slate-700 rounded-lg p-4 cursor-pointer hover:bg-slate-800 transition-colors flex flex-col items-center justify-center min-h-[100px]"
            >
                {referenceImage ? (
                    <div className="relative w-full h-32">
                        <img src={referenceImage} alt="Ref" className="w-full h-full object-contain rounded" />
                        <button 
                            onClick={(e) => { e.stopPropagation(); setReferenceImage(null); }}
                            className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </div>
                ) : (
                    <div className="text-center text-slate-500">
                        <Upload className="w-8 h-8 mx-auto mb-2" />
                        <span className="text-xs">Clique para upload (Img2Img)</span>
                    </div>
                )}
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
            </div>
        </div>

        {/* Prompt */}
        <div className="space-y-2 flex-1 flex flex-col relative">
            <div className="flex justify-between items-end">
                <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-slate-300">Descrição do Prompt</label>
                    <button 
                        onClick={() => setShowHistory(!showHistory)}
                        className={`text-xs flex items-center gap-1 transition-colors ${showHistory ? 'text-purple-400' : 'text-slate-500 hover:text-slate-300'}`}
                        title="Histórico de Prompts"
                    >
                        <History className="w-3 h-3" />
                    </button>
                </div>
                <button 
                    onClick={handleEnhancePrompt}
                    disabled={isEnhancing || !prompt.trim()}
                    className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 disabled:opacity-50"
                    title="Melhorar prompt com IA"
                >
                    {isEnhancing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                    Mágica
                </button>
            </div>
            
            {/* History Dropdown */}
            {showHistory && (
                <div className="absolute top-8 left-0 right-0 z-20 bg-slate-800 border border-slate-600 rounded-lg shadow-xl max-h-60 overflow-y-auto">
                    <div className="p-2 border-b border-slate-700 flex justify-between items-center sticky top-0 bg-slate-800">
                        <span className="text-xs font-bold text-slate-400 flex items-center gap-1"><Clock className="w-3 h-3" /> Recentes</span>
                        <button onClick={() => setShowHistory(false)} className="text-slate-500 hover:text-white"><X className="w-3 h-3" /></button>
                    </div>
                    {promptHistory.length === 0 ? (
                        <div className="p-4 text-center text-xs text-slate-500 italic">Nenhum histórico recente.</div>
                    ) : (
                        <div className="flex flex-col">
                            {promptHistory.map((hist, idx) => (
                                <button 
                                    key={idx}
                                    onClick={() => { setPrompt(hist); setShowHistory(false); }}
                                    className="text-left px-3 py-2 text-xs text-slate-300 hover:bg-slate-700 hover:text-white border-b border-slate-700/50 last:border-0 truncate"
                                    title={hist}
                                >
                                    {hist}
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <div className="relative flex-1">
                {isDescribing && (
                    <div className="absolute inset-0 bg-slate-900/80 z-10 flex items-center justify-center gap-2 text-blue-300 text-sm">
                        <Loader2 className="w-4 h-4 animate-spin" /> Analisando Imagem...
                    </div>
                )}
                <textarea 
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Descreva sua cena, iluminação, cores e assunto..."
                    className="w-full h-full bg-slate-800 border border-slate-600 rounded p-3 text-white focus:ring-2 focus:ring-purple-500 outline-none resize-none text-sm min-h-[120px]"
                />
            </div>
        </div>

        <button 
            onClick={handleGenerate}
            disabled={isGenerating || isEditing || !prompt.trim()}
            className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:text-slate-500 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-purple-900/50"
        >
            {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Wand2 className="w-5 h-5" />}
            {isGenerating ? 'Renderizando...' : 'Gerar Arte'}
        </button>
      </div>

      {/* Right Panel: Result */}
      <div className="flex-1 bg-black/20 rounded-xl border border-slate-700/50 flex flex-col items-center justify-center relative p-6">
        {error ? (
            <div className="flex flex-col items-center justify-center text-center p-8 max-w-md bg-red-900/20 border border-red-500/50 rounded-xl animate-in fade-in zoom-in duration-300">
                <div className="w-16 h-16 bg-red-900/50 rounded-full flex items-center justify-center mb-4">
                    <Zap className="w-8 h-8 text-red-500" />
                </div>
                <h3 className="text-xl font-bold text-red-200 mb-2">Falha na Geração</h3>
                <p className="text-red-200/80 mb-6">{error}</p>
                <button 
                    onClick={() => setError(null)}
                    className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-bold transition-colors"
                >
                    Tentar Novamente
                </button>
            </div>
        ) : generatedResult ? (
            <div className="flex flex-col items-center w-full h-full max-w-4xl gap-4">
                {/* Result Container */}
                <div className={`relative w-full h-full bg-slate-900 rounded-lg overflow-hidden border border-slate-600 shadow-2xl group flex items-center justify-center`}>
                     
                     {/* Loading Overlay */}
                     {(isGenerating || isEditing) && (
                        <div className="absolute inset-0 bg-black/80 z-50 flex flex-col items-center justify-center gap-2">
                             <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
                             <span className="text-sm font-bold text-purple-200">{isEditing ? "Refinando..." : "Renderizando..."}</span>
                        </div>
                     )}

                     {/* Edit Input Overlay */}
                     {showEditInput && !isEditing && (
                        <div className="absolute inset-0 bg-slate-900/90 z-40 flex flex-col p-6 items-center justify-center">
                             <div className="w-full max-w-md space-y-3">
                                <div className="flex justify-between items-center text-white">
                                    <h3 className="font-bold flex items-center gap-2"><Wand2 className="w-4 h-4 text-purple-400" /> Correção Mágica / Editar</h3>
                                    <button onClick={() => setShowEditInput(false)} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
                                </div>
                                <textarea 
                                    value={editInstruction}
                                    onChange={(e) => setEditInstruction(e.target.value)}
                                    placeholder="Instrução (ex: Mude o céu para roxo, adicione um dragão)"
                                    className="w-full h-24 bg-black border border-slate-700 rounded-lg p-3 text-white resize-none outline-none focus:border-purple-500 text-sm"
                                    autoFocus
                                />
                                <div className="flex gap-2">
                                    <button 
                                        onClick={() => setShowEditInput(false)}
                                        className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 py-2 rounded-lg font-bold text-sm"
                                    >
                                        Cancelar
                                    </button>
                                    <button 
                                        onClick={handleEdit}
                                        disabled={!editInstruction.trim()}
                                        className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:text-slate-500 text-white py-2 rounded-lg font-bold text-sm"
                                    >
                                        Aplicar Correção
                                    </button>
                                </div>
                             </div>
                        </div>
                     )}

                     <img 
                        src={generatedResult.imageUrl} 
                        alt="Result" 
                        referrerPolicy="no-referrer"
                        className="max-w-full max-h-full object-contain cursor-pointer" 
                        onClick={() => onImageClick?.(generatedResult)}
                     />
                     
                     {/* Hover Controls */}
                     {!showEditInput && !isEditing && !isGenerating && (
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                            <button 
                                onClick={handleDownload}
                                className="px-4 py-2 bg-white text-slate-900 rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                            >
                                <Download className="w-4 h-4" /> Baixar
                            </button>
                            <button 
                                onClick={handleGenerate}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                            >
                                <RefreshCw className="w-4 h-4" /> Re-rolar
                            </button>
                            <button 
                                onClick={() => setShowEditInput(true)}
                                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                            >
                                <Wand2 className="w-4 h-4" /> Editar
                            </button>
                            {/* Reverse Prompt for Generated Image */}
                            <button 
                                onClick={handleDescribeImage}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                                title="Descrever o que tem na imagem"
                            >
                                {isDescribing ? <Loader2 className="w-4 h-4 animate-spin" /> : <ScanEye className="w-4 h-4" />} Descrever
                            </button>
                            <button 
                                onClick={handleAnalyzeGeneratedImage}
                                className="px-4 py-2 bg-purple-700 hover:bg-purple-600 text-white rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                                title="Extrair um prompt de estilo detalhado desta imagem"
                            >
                                {isAnalyzing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />} Analisar Estilo
                            </button>
                        </div>
                     )}
                </div>
            </div>
        ) : (
            <div className="text-slate-600 flex flex-col items-center justify-center h-full opacity-60">
                <div className="w-24 h-24 rounded-full bg-slate-800/50 flex items-center justify-center mb-6 border border-slate-700">
                    <Palette className="w-10 h-10" />
                </div>
                <p className="text-xl font-medium text-slate-400">Tela em Branco</p>
                <p className="text-sm mt-2 max-w-xs text-center">
                    Selecione um estilo, defina sua proporção e descreva sua visão. 
                </p>
            </div>
        )}
      </div>
    </div>
  );
};

export default ImageStudio;