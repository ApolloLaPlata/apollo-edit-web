import React, { useState, useRef } from 'react';
import { ApiKey, GeneratedImage, GenerationSettings, Character } from '../types';
import { generateThumbnail, editGeneratedImage } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { MonitorPlay, Smartphone, Type, Layers, Download, Loader2, X, Zap, RefreshCw, Palette, MessageSquare, Plus, Wand2 } from 'lucide-react';
import { THUMBNAIL_STYLES, MODELS } from '../constants';
import CharacterSelector from './CharacterSelector';

interface ThumbnailStudioProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  addGeneratedImage: (img: GeneratedImage) => void;
  characters: Character[];
  settings?: GenerationSettings;
  onImageClick?: (image: GeneratedImage) => void;
}

const ThumbnailStudio: React.FC<ThumbnailStudioProps> = ({ apiKeys, setApiKeys, addGeneratedImage, characters, onImageClick }) => {
  // Mode Switcher
  const [mode, setMode] = useState<'structured' | 'custom'>('structured');
  // Model Selector (Default to Flash 2.5)
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');

  // Inputs - Structured
  const [titleText, setTitleText] = useState('');
  const [hookText, setHookText] = useState('');
  const [backgroundDesc, setBackgroundDesc] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('mrbeast');
  const [subjectPosition, setSubjectPosition] = useState<'left' | 'right' | 'center'>('right');
  const [textColor, setTextColor] = useState('White & Red');
  
  // Inputs - Custom
  const [customPrompt, setCustomPrompt] = useState('');

  // Shared Inputs
  const [referenceImages, setReferenceImages] = useState<string[]>([]);
  const [layout, setLayout] = useState<'horizontal' | 'vertical'>('horizontal');
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);

  // Processing
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<GeneratedImage | null>(null);

  // Edit Mode
  const [isEditing, setIsEditing] = useState(false);
  const [showEditInput, setShowEditInput] = useState(false);
  const [editInstruction, setEditInstruction] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const apiKeysRef = useRef(apiKeys);
  React.useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      files.forEach((file) => {
        const reader = new FileReader();
        reader.onload = (ev) => {
          const res = ev.target?.result as string;
          if (res) {
            setReferenceImages((prev) => [...prev, res]);
          }
        };
        reader.readAsDataURL(file as Blob);
      });
      
      // Reset input to allow selecting the same files again if needed
      if (fileInputRef.current) {
          fileInputRef.current.value = '';
      }
    }
  };

  const removeReferenceImage = (index: number) => {
      setReferenceImages(prev => prev.filter((_, i) => i !== index));
  };

  const toggleCharacter = (id: string) => {
      setSelectedCharacterIds(prev => 
          prev.includes(id) ? prev.filter(cId => cId !== id) : [...prev, id]
      );
  };

  const handleGenerate = async (overrideLayout?: 'horizontal' | 'vertical') => {
      const targetLayout = overrideLayout || layout;
      
      // Validation based on mode
      if (mode === 'structured') {
          if (!titleText && !backgroundDesc) {
              toast.error("Preencha pelo menos o Título ou o Fundo.");
              return;
          }
      } else {
          if (!customPrompt.trim()) {
              toast.error("Insira um prompt descritivo para a thumbnail.");
              return;
          }
      }

      setIsGenerating(true);
      setShowEditInput(false);
      
      const stylePrompt = THUMBNAIL_STYLES.find(s => s.id === selectedStyle)?.prompt || "";
      const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));
      
      try {
          let imageUrl = "";

          imageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await generateThumbnail(apiKey, {
                  titleText,
                  hookText,
                  backgroundDesc,
                  referenceImages, // Pass array
                  characters: selectedCharacters,
                  stylePrompt,
                  textColor,
                  layout: targetLayout,
                  subjectPosition,
                  customPrompt: mode === 'custom' ? customPrompt : undefined,
                  modelId: selectedModel // Pass selected model
              })
          );

          const promptLabel = mode === 'custom' ? `[Custom Thumb] ${customPrompt.slice(0, 30)}...` : `[Thumbnail] ${titleText}`;

          // Save to Gallery
          const galleryItem: GeneratedImage = {
              id: crypto.randomUUID(),
              prompt: `${promptLabel} (${targetLayout})`,
              imageUrl: imageUrl,
              timestamp: Date.now(),
              characterIds: selectedCharacterIds,
              aspectRatio: targetLayout === 'horizontal' ? '16:9' : '9:16'
          };
          
          setGeneratedResult(galleryItem);
          addGeneratedImage(galleryItem);

          // If we forced a layout change (e.g. converting), update state
          if (overrideLayout) setLayout(overrideLayout);

      } catch (e: any) {
          toast.error("Erro: " + e.message);
      } finally {
          setIsGenerating(false);
      }
  };

  const handleEdit = async () => {
    if (!generatedResult || !editInstruction.trim()) return;
    
    setIsEditing(true);

    const tempSettings: any = {
        modelId: selectedModel, // Use the selected model for consistency
        aspectRatio: layout === 'horizontal' ? '16:9' : '9:16',
    };

    try {
        const newImageUrl = await executeWithKeyRotation(
            apiKeysRef,
            setApiKeys,
            async (apiKey) => await editGeneratedImage(apiKey, generatedResult.imageUrl, editInstruction, tempSettings)
        );

        const galleryItem: GeneratedImage = {
          id: crypto.randomUUID(),
          prompt: `[Editado Thumb: ${editInstruction}]`,
          imageUrl: newImageUrl,
          timestamp: Date.now(),
          characterIds: [],
          aspectRatio: layout === 'horizontal' ? '16:9' : '9:16'
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

  const handleGetPrompt = async () => {
    if (!generatedResult) return;

    try {
        const description = await executeWithKeyRotation(
            apiKeysRef,
            setApiKeys,
            async (apiKey) => await import('../services/geminiService').then(m => m.describeImage(apiKey, generatedResult.imageUrl))
        );
        
        // Switch to custom mode to show the prompt
        setMode('custom');
        setCustomPrompt(description);
        
    } catch (error: any) {
        toast.error("Falha ao obter prompt: " + error.message);
    }
  };

  const handleDownload = () => {
      if (generatedResult) {
          const link = document.createElement('a');
          link.href = generatedResult.imageUrl;
          link.download = `thumbnail_${layout}_${Date.now()}.png`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
      }
  };

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 p-2">
      {/* LEFT: Controls */}
      <div className="w-full md:w-1/3 bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-6 overflow-y-auto">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
                <MonitorPlay className="w-6 h-6 text-orange-400" />
                Thumbnail Creator
            </h2>
            <p className="text-xs text-slate-400">
                Gere miniaturas otimizadas para YouTube (16:9) e Shorts/TikTok (9:16) com controle de layout e texto.
            </p>
          </div>

          {/* Mode Switcher */}
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 gap-1">
             <button
                onClick={() => setMode('structured')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${mode === 'structured' ? 'bg-orange-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
             >
                 <Layers className="w-4 h-4" /> Designer
             </button>
             <button
                onClick={() => setMode('custom')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${mode === 'custom' ? 'bg-orange-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
             >
                 <MessageSquare className="w-4 h-4" /> Prompt Livre
             </button>
          </div>

          {/* Model Selection & Style */}
          <div className="grid grid-cols-2 gap-3">
              <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                    <Zap className="w-3 h-3 text-yellow-500" /> Modelo
                </label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-600 rounded px-2 py-2 text-white text-xs focus:ring-2 focus:ring-purple-500 outline-none"
                >
                  {MODELS.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                    <Palette className="w-3 h-3 text-purple-400" /> Estilo
                </label>
                <select
                    value={selectedStyle}
                    onChange={(e) => setSelectedStyle(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-600 rounded px-2 py-2 text-white text-xs outline-none"
                >
                    {THUMBNAIL_STYLES.map(s => (
                        <option key={s.id} value={s.id}>{s.label}</option>
                    ))}
                </select>
              </div>
          </div>

          {/* Format Toggle (Always Visible) */}
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 gap-1">
             <button
                onClick={() => setLayout('horizontal')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${layout === 'horizontal' ? 'bg-slate-700 text-white border border-slate-500' : 'text-slate-500 hover:text-slate-300'}`}
             >
                 <MonitorPlay className="w-4 h-4" /> Horizontal (16:9)
             </button>
             <button
                onClick={() => setLayout('vertical')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex items-center justify-center gap-2 ${layout === 'vertical' ? 'bg-slate-700 text-white border border-slate-500' : 'text-slate-500 hover:text-slate-300'}`}
             >
                 <Smartphone className="w-4 h-4" /> Vertical (9:16)
             </button>
          </div>

            {/* Characters */}
            {characters.length === 0 ? (
                <div className="text-sm text-slate-500 italic bg-slate-950 p-3 rounded-lg border border-slate-800">
                    Nenhum personagem cadastrado. Vá na aba Personagens para criar.
                </div>
            ) : (
                <CharacterSelector 
                    characters={characters}
                    onSelect={(char) => toggleCharacter(char.id)}
                    mode="toggle"
                    selectedIds={selectedCharacterIds}
                    label="Personagens"
                />
            )}

          {/* SHARED: Multiple Reference Images */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-400 uppercase flex justify-between">
                <span>Imagens de Referência ({referenceImages.length})</span>
                <span className="text-[10px] text-orange-400">Estilo & Composição</span>
            </label>
            
            {/* Gallery Grid */}
            <div className="grid grid-cols-4 gap-2">
                {referenceImages.map((img, idx) => (
                    <div key={idx} className="relative group aspect-square rounded overflow-hidden border border-slate-600">
                        <img src={img} alt={`Ref ${idx}`} className="w-full h-full object-cover" />
                        <button 
                            onClick={() => removeReferenceImage(idx)}
                            className="absolute top-1 right-1 bg-red-500/80 hover:bg-red-500 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                            <X className="w-3 h-3" />
                        </button>
                    </div>
                ))}
                
                {/* Add Button */}
                <div 
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors flex flex-col items-center justify-center aspect-square text-slate-500 hover:text-orange-400"
                >
                    <Plus className="w-6 h-6" />
                </div>
            </div>
            <input 
                ref={fileInputRef} 
                type="file" 
                accept="image/*" 
                multiple 
                className="hidden" 
                onChange={handleFileChange} 
            />
          </div>

          <hr className="border-slate-800" />

          {/* CONDITIONAL INPUTS */}
          {mode === 'structured' ? (
              <>
                {/* Text Controls */}
                <div className="space-y-3 bg-slate-800/50 p-3 rounded-lg border border-slate-700">
                    <label className="text-xs font-bold text-slate-400 uppercase flex items-center gap-2">
                        <Type className="w-3 h-3" /> Tipografia & Texto
                    </label>
                    <input 
                        value={titleText}
                        onChange={(e) => setTitleText(e.target.value)}
                        placeholder="MANCHETE PRINCIPAL (Curta)"
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white font-bold text-sm outline-none focus:border-orange-500"
                    />
                    <input 
                        value={hookText}
                        onChange={(e) => setHookText(e.target.value)}
                        placeholder="Hook / Gancho Secundário"
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm outline-none focus:border-orange-500"
                    />
                    <select
                        value={textColor}
                        onChange={(e) => setTextColor(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-600 rounded px-2 py-1 text-xs text-slate-300 outline-none"
                    >
                        <option value="White & Red">Branco & Vermelho (Padrão)</option>
                        <option value="Yellow & Black">Amarelo & Preto (Aviso)</option>
                        <option value="Neon Green">Verde Neon (Gaming)</option>
                        <option value="Gold & White">Dourado & Branco (Luxo)</option>
                        <option value="White with Black Stroke">Branco c/ Borda Preta (Meme)</option>
                    </select>
                </div>

                {/* Composition */}
                <div className="grid grid-cols-2 gap-3">
                    <div>
                        <label className="text-[10px] font-bold text-slate-400 uppercase block mb-1">Posição do Sujeito</label>
                        <select
                            value={subjectPosition}
                            onChange={(e) => setSubjectPosition(e.target.value as any)}
                            className="w-full bg-slate-800 border border-slate-600 rounded px-2 py-2 text-white text-xs outline-none"
                        >
                            <option value="right">Direita (Padrão)</option>
                            <option value="left">Esquerda</option>
                            <option value="center">Centro</option>
                        </select>
                    </div>
                    {/* Style Selector moved to shared area */}
                </div>

                {/* Background */}
                <div>
                    <label className="text-xs font-bold text-slate-400 uppercase block mb-1">Descrição do Fundo</label>
                    <textarea 
                        value={backgroundDesc}
                        onChange={(e) => setBackgroundDesc(e.target.value)}
                        placeholder="Ex: Explosão, Escritório minimalista, Cidade futurista, Fundo degradê roxo..."
                        className="w-full h-20 bg-slate-800 border border-slate-600 rounded p-2 text-white text-sm resize-none outline-none focus:border-orange-500"
                    />
                </div>
              </>
          ) : (
              // Custom Mode Inputs
              <div className="flex-1 flex flex-col gap-2">
                 <label className="text-xs font-bold text-slate-400 uppercase block mb-1">Prompt de Thumbnail Detalhado</label>
                 <textarea 
                    value={customPrompt}
                    onChange={(e) => setCustomPrompt(e.target.value)}
                    placeholder={`Descreva a thumbnail completa.\nEx: Uma mão segurando um iPhone quebrado com tela rachada, fundo de chamas desfocado. Texto grande amarelo escrito "PERDI TUDO" no topo.`}
                    className="w-full h-48 bg-slate-800 border border-slate-600 rounded p-3 text-white text-sm resize-none outline-none focus:border-orange-500 font-mono"
                 />
                 <p className="text-[10px] text-slate-500">
                    O modelo ainda respeitará o formato {layout === 'horizontal' ? '16:9' : '9:16'} e tentará incluir qualquer texto mencionado no prompt.
                 </p>
              </div>
          )}

          <button 
                onClick={() => handleGenerate()}
                disabled={isGenerating}
                className="w-full bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-500 hover:to-red-500 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-orange-900/50 transition-all transform hover:scale-[1.02]"
            >
                {isGenerating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
                {isGenerating ? 'Renderizando Design...' : 'Gerar Thumbnail'}
            </button>
      </div>

      {/* RIGHT: Preview */}
      <div className="flex-1 bg-black/30 rounded-xl border border-slate-700/50 p-6 flex flex-col items-center justify-center relative">
          {generatedResult ? (
              <div className="flex flex-col gap-4 items-center w-full max-w-4xl h-full">
                  <div className={`relative bg-slate-900 rounded-lg overflow-hidden border border-slate-600 shadow-2xl group flex items-center justify-center w-full h-full p-2`}>
                        
                        {/* Edit Input Overlay */}
                        {showEditInput && !isEditing && (
                        <div className="absolute inset-0 bg-slate-900/95 z-50 flex flex-col p-6 items-center justify-center">
                             <div className="w-full max-w-md space-y-3">
                                <div className="flex justify-between items-center text-white">
                                    <h3 className="font-bold flex items-center gap-2"><Wand2 className="w-4 h-4 text-orange-400" /> Correção de Thumbnail</h3>
                                    <button onClick={() => setShowEditInput(false)} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
                                </div>
                                <textarea 
                                    value={editInstruction}
                                    onChange={(e) => setEditInstruction(e.target.value)}
                                    placeholder="Instrução (ex: Corrija o texto para 'VIRAL', mude a cor da camisa para azul, remova o objeto do fundo...)"
                                    className="w-full h-24 bg-black border border-slate-700 rounded-lg p-3 text-white resize-none outline-none focus:border-orange-500 text-sm"
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
                                        className="flex-1 bg-orange-600 hover:bg-orange-700 disabled:bg-slate-700 disabled:text-slate-500 text-white py-2 rounded-lg font-bold text-sm"
                                    >
                                        Aplicar Correção
                                    </button>
                                </div>
                             </div>
                        </div>
                     )}

                     {/* Loading Overlay */}
                     {(isGenerating || isEditing) && (
                        <div className="absolute inset-0 bg-black/80 z-50 flex flex-col items-center justify-center gap-2">
                             <Loader2 className="w-8 h-8 animate-spin text-orange-400" />
                             <span className="text-sm font-bold text-orange-200">{isEditing ? "Refinando..." : "Renderizando..."}</span>
                        </div>
                     )}

                        <img 
                            src={generatedResult.imageUrl} 
                            alt="Thumbnail" 
                            referrerPolicy="no-referrer"
                            className={`object-contain shadow-black/50 shadow-2xl cursor-pointer ${layout === 'horizontal' ? 'aspect-video w-full' : 'aspect-[9/16] h-full'}`} 
                            onClick={() => onImageClick?.(generatedResult)}
                        />
                        
                        {/* Hover Overlay */}
                        {!showEditInput && !isEditing && !isGenerating && (
                            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                                <button 
                                    onClick={handleDownload}
                                    className="px-4 py-2 bg-white text-slate-900 rounded-full font-bold text-sm hover:scale-105 transition-transform flex items-center gap-2 shadow-lg"
                                >
                                    <Download className="w-4 h-4" /> Baixar
                                </button>
                                <button 
                                    onClick={() => handleGenerate()}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-full font-bold text-sm hover:scale-105 transition-transform flex items-center gap-2 shadow-lg"
                                >
                                    <RefreshCw className="w-4 h-4" /> Regenerar
                                </button>
                                <button 
                                    onClick={() => setShowEditInput(true)}
                                    className="px-4 py-2 bg-purple-600 text-white rounded-full font-bold text-sm hover:scale-105 transition-transform flex items-center gap-2 shadow-lg"
                                >
                                    <Wand2 className="w-4 h-4" /> Editar
                                </button>
                                <button 
                                    onClick={handleGetPrompt}
                                    className="px-4 py-2 bg-emerald-600 text-white rounded-full font-bold text-sm hover:scale-105 transition-transform flex items-center gap-2 shadow-lg"
                                >
                                    <MessageSquare className="w-4 h-4" /> Obter Prompt
                                </button>
                            </div>
                        )}
                  </div>

                  {/* Cross-Format Generation Bar */}
                  <div className="w-full bg-slate-800 p-4 rounded-xl border border-slate-700 flex justify-between items-center">
                      <div className="flex flex-col">
                          <span className="text-white font-bold text-sm">Geração Cruzada</span>
                          <span className="text-xs text-slate-400">Gostou? Gere a versão {layout === 'horizontal' ? 'Vertical' : 'Horizontal'} mantendo o estilo.</span>
                      </div>
                      <button 
                        onClick={() => handleGenerate(layout === 'horizontal' ? 'vertical' : 'horizontal')}
                        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
                      >
                          {layout === 'horizontal' ? <Smartphone className="w-4 h-4" /> : <MonitorPlay className="w-4 h-4" />}
                          Gerar Versão {layout === 'horizontal' ? 'Vertical' : 'Horizontal'}
                      </button>
                  </div>
              </div>
          ) : (
              <div className="text-slate-600 flex flex-col items-center justify-center h-full opacity-60">
                <div className="w-24 h-24 rounded-full bg-slate-800/50 flex items-center justify-center mb-6 border border-slate-700">
                    <Layers className="w-10 h-10" />
                </div>
                <p className="text-xl font-medium text-slate-400">Thumbnail Studio</p>
                <p className="text-sm mt-2 max-w-xs text-center">
                    Crie capas de alto impacto. Insira um título, uma foto e deixe a IA cuidar da composição.
                </p>
            </div>
          )}
      </div>
    </div>
  );
};

export default ThumbnailStudio;