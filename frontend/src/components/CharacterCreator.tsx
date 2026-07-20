import React, { useState, useRef } from 'react';
import { ApiKey, Character, GeneratedImage, GenerationSettings } from '../types';
import { generateCharacterSheet, editGeneratedImage, describeImage, expandCharacterDescription } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Wand2, Upload, Loader2, Save, X, Image as ImageIcon, Accessibility, CheckCircle2, Zap, RefreshCw, Smile, ScanEye, Download, Sparkles } from 'lucide-react';
import { MODELS } from '../constants';

interface CharacterCreatorProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  onSaveCharacter: (char: Character) => void;
  addGeneratedImage: (img: GeneratedImage) => void;
  settings: GenerationSettings;
}

const CharacterCreator: React.FC<CharacterCreatorProps> = ({ apiKeys, setApiKeys, onSaveCharacter, addGeneratedImage, settings }) => {
  const [prompt, setPrompt] = useState('');
  const [referenceImage, setReferenceImage] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDescribing, setIsDescribing] = useState(false);
  const [isExpanding, setIsExpanding] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<string | null>(null);
  const [newCharName, setNewCharName] = useState('');
  const [newCharDescription, setNewCharDescription] = useState('');
  const [mode, setMode] = useState<'turnaround' | 't-pose' | 'expression'>('turnaround');
  // Default to Flash 2.5 for stability
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');
  
  // Edit Mode State
  const [isEditing, setIsEditing] = useState(false);
  const [showEditInput, setShowEditInput] = useState(false);
  const [editInstruction, setEditInstruction] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);
  const apiKeysRef = useRef(apiKeys);
  React.useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (ev) => {
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            let width = img.width;
            let height = img.height;
            const maxDim = 1024;

            if (width > height && width > maxDim) {
                height *= maxDim / width;
                width = maxDim;
            } else if (height > maxDim) {
                width *= maxDim / height;
                height = maxDim;
            }

            canvas.width = width;
            canvas.height = height;
            const ctx = canvas.getContext('2d');
            if (ctx) {
                ctx.drawImage(img, 0, 0, width, height);
                setReferenceImage(canvas.toDataURL(file.type || 'image/jpeg', 0.8));
            } else {
                setReferenceImage(ev.target?.result as string);
            }
        };
        img.src = ev.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const handleMagicExpand = async () => {
      if (!prompt.trim()) return;

      setIsExpanding(true);
      try {
          const expanded = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await expandCharacterDescription(prompt, mode, settings, apiKey)
          );
          setPrompt(expanded);
      } catch (error: any) {
          toast.error("Falha ao expandir descrição: " + error.message);
      } finally {
          setIsExpanding(false);
      }
  };

  const handleDescribeImage = async () => {
      if (!referenceImage) return;

      setIsDescribing(true);
      try {
          const description = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await describeImage(apiKey, referenceImage)
          );
          setPrompt(description);
      } catch (error: any) {
          toast.error("Falha ao descrever imagem: " + error.message);
      } finally {
          setIsDescribing(false);
      }
  };

  const handleDescribeResult = async () => {
      if (!generatedResult) return;

      setIsDescribing(true);
      try {
          const description = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await describeImage(apiKey, generatedResult)
          );
          setNewCharDescription(description);
          toast.success("Descrição do personagem gerada com sucesso!");
      } catch (error: any) {
          toast.error("Falha ao descrever resultado: " + error.message);
      } finally {
          setIsDescribing(false);
      }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setGeneratedResult(null);
    setShowEditInput(false);

    try {
        let imageUrl = "";

        // Gemini Generation
        imageUrl = await executeWithKeyRotation(
            apiKeysRef,
            setApiKeys,
            async (apiKey) => await generateCharacterSheet(apiKey, prompt, referenceImage, selectedModel, mode)
        );

        setGeneratedResult(imageUrl);

        let promptPrefix = '';
        if (mode === 't-pose') promptPrefix = '[T-Pose]';
        else if (mode === 'expression') promptPrefix = '[Expressions]';
        else promptPrefix = '[Character Sheet]';

        // Save to gallery automatically as a backup
        const galleryItem: GeneratedImage = {
            id: crypto.randomUUID(),
            prompt: `${promptPrefix} ${prompt}`,
            imageUrl: imageUrl,
            timestamp: Date.now(),
            characterIds: [],
            aspectRatio: mode === 'turnaround' ? '16:9' : '1:1'
        };
        addGeneratedImage(galleryItem);

    } catch (error: any) {
        toast.error("Falha na geração: " + error.message);
    } finally {
        setIsGenerating(false);
    }
  };

  const handleEdit = async () => {
      if (!generatedResult || !editInstruction.trim()) return;
      
      setIsEditing(true);

      // Construct temporary settings to pass to the service
      const tempSettings: any = {
          modelId: selectedModel,
          aspectRatio: mode === 'turnaround' ? '16:9' : '1:1',
      };

      try {
          const newImageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await editGeneratedImage(apiKey, generatedResult, editInstruction, tempSettings)
          );
          
          setGeneratedResult(newImageUrl);
          
          let promptPrefix = '';
          if (mode === 't-pose') promptPrefix = '[T-Pose]';
          else if (mode === 'expression') promptPrefix = '[Expressions]';
          else promptPrefix = '[Character Sheet]';

          // Save edited version to gallery
          const galleryItem: GeneratedImage = {
            id: crypto.randomUUID(),
            prompt: `[Editado: ${editInstruction}] ${promptPrefix} ${prompt}`,
            imageUrl: newImageUrl,
            timestamp: Date.now(),
            characterIds: [],
            aspectRatio: mode === 'turnaround' ? '16:9' : '1:1'
        };
        addGeneratedImage(galleryItem);
        
        // Reset edit UI
        setShowEditInput(false);
        setEditInstruction('');

      } catch (error: any) {
          toast.error("Edição falhou: " + error.message);
      } finally {
          setIsEditing(false);
      }
  };

  const handleSaveToRoster = () => {
      if (!generatedResult) return;
      
      const name = newCharName.trim() || `Novo Personagem`;
      const finalName = name.startsWith('#') ? name : `#${name}`;

      const newChar: Character = {
          id: crypto.randomUUID(),
          name: finalName,
          description: newCharDescription.trim(),
          images: [generatedResult],
          previewUrl: generatedResult
      };

      onSaveCharacter(newChar);
      toast.success(`Salvo ${finalName} na Lista!`);
      
      // Reset
      setNewCharName('');
      setNewCharDescription('');
      setGeneratedResult(null);
      setPrompt('');
      setReferenceImage(null);
      setShowEditInput(false);
  };

  const handleDownload = () => {
    if (generatedResult) {
        const link = document.createElement('a');
        link.href = generatedResult;
        link.download = `character_${mode}_${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
  };

  const getPlaceholder = () => {
      if (mode === 't-pose') {
          return "Ex: Um ninja ciborgue, simetria, mãos abertas, rosto neutro, detalhes mecânicos visíveis...";
      } else if (mode === 'expression') {
          return "Ex: Um elfo ladino alegre. Mostrar expressões: Rindo, Chorando, Com Raiva, Suspeito. Poses: Pulando, ataque com adaga...";
      } else {
          return "Ex: Um samurai cyberpunk com armadura verde neon, katana nas costas, expressão séria...";
      }
  };

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 p-2">
      {/* Left Panel: Inputs */}
      <div className="w-full md:w-1/3 bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-6 overflow-y-auto">
        <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
                <Wand2 className="w-6 h-6 text-purple-400" />
                Laboratório de Personagens
            </h2>
            <p className="text-sm text-slate-400">
                Crie novos personagens com foco na consistência. Escolha entre uma folha de giro completo, uma Pose em T para rigging ou uma folha de expressões.
            </p>
        </div>

        {/* Model Selection */}
        <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
            <label className="text-xs font-bold text-slate-400 uppercase mb-2 block flex items-center gap-2">
                <Zap className="w-3 h-3 text-yellow-500" /> Modelo de Geração
            </label>
            <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm focus:ring-2 focus:ring-purple-500 outline-none"
            >
                {MODELS.map((m) => (
                    <option key={m.id} value={m.id}>
                    {m.name}
                    </option>
                ))}
            </select>
        </div>

        {/* Mode Selector */}
        <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 gap-1">
            <button
                onClick={() => setMode('turnaround')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex flex-col items-center justify-center gap-1 ${mode === 'turnaround' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}
                title="Giro de Corpo Completo (16:9)"
            >
                <ImageIcon className="w-4 h-4" /> Giro 360
            </button>
            <button
                onClick={() => setMode('t-pose')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex flex-col items-center justify-center gap-1 ${mode === 't-pose' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}
                title="Referência para Rigging (1:1)"
            >
                <Accessibility className="w-4 h-4" /> Pose em T
            </button>
            <button
                onClick={() => setMode('expression')}
                className={`flex-1 py-2 text-xs font-bold rounded-md transition-all flex flex-col items-center justify-center gap-1 ${mode === 'expression' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700/50'}`}
                title="Expressões e Poses (1:1)"
            >
                <Smile className="w-4 h-4" /> Poses
            </button>
        </div>

        {/* Reference Image */}
        <div className="space-y-2">
            <div className="flex justify-between items-end">
                <label className="text-sm font-medium text-slate-300">Imagem de Referência (Opcional)</label>
                {referenceImage && (
                    <button 
                        onClick={handleDescribeImage}
                        disabled={isDescribing}
                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
                        title="Usar IA para descrever esta imagem e preencher o prompt"
                    >
                        {isDescribing ? <Loader2 className="w-3 h-3 animate-spin" /> : <ScanEye className="w-3 h-3" />}
                        {isDescribing ? "Analisando..." : "Obter Prompt da Imagem"}
                    </button>
                )}
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
                        <span className="text-xs">Clique para enviar base de estilo/sketch</span>
                    </div>
                )}
                <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
            </div>
        </div>

        {/* Prompt */}
        <div className="space-y-2 flex-1 flex flex-col">
            <div className="flex justify-between items-end">
                <label className="text-sm font-medium text-slate-300">Descrição do Personagem</label>
                <button 
                    onClick={handleMagicExpand}
                    disabled={isExpanding || !prompt.trim()}
                    className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 transition-colors disabled:opacity-50"
                    title="Usar IA para expandir e detalhar sua descrição"
                >
                    {isExpanding ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
                    {isExpanding ? "Expandindo..." : "Expandir com IA"}
                </button>
            </div>
            <div className="relative flex-1">
                {isDescribing && (
                    <div className="absolute inset-0 bg-slate-900/80 z-10 flex items-center justify-center gap-2 text-blue-300 text-sm backdrop-blur-sm rounded">
                        <Loader2 className="w-4 h-4 animate-spin" /> Gerando Prompt Visual...
                    </div>
                )}
                <textarea 
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder={getPlaceholder()}
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
            {isGenerating ? 'Gerando...' : 'Gerar Folha'}
        </button>
      </div>

      {/* Right Panel: Result */}
      <div className="flex-1 bg-black/20 rounded-xl border border-slate-700/50 flex flex-col items-center justify-center relative p-6">
        {generatedResult ? (
            <div className="flex flex-col items-center w-full h-full max-w-4xl gap-4">
                {/* Result Container - Adapts to aspect ratio */}
                <div className={`relative w-full ${mode === 'turnaround' ? 'aspect-video' : 'aspect-square max-w-xl'} bg-slate-900 rounded-lg overflow-hidden border border-slate-600 shadow-2xl group`}>
                     
                     {/* Loading Overlay for Edit */}
                     {(isGenerating || isEditing) && (
                        <div className="absolute inset-0 bg-black/80 z-50 flex flex-col items-center justify-center gap-2">
                             <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
                             <span className="text-sm font-bold text-purple-200">{isEditing ? "Refinando Imagem..." : "Gerando..."}</span>
                        </div>
                     )}

                     {/* Edit Input Overlay */}
                     {showEditInput && !isEditing && (
                        <div className="absolute inset-0 bg-slate-900/90 z-40 flex flex-col p-6 items-center justify-center">
                             <div className="w-full max-w-md space-y-3">
                                <div className="flex justify-between items-center text-white">
                                    <h3 className="font-bold flex items-center gap-2"><Wand2 className="w-4 h-4 text-purple-400" /> Descreva a Correção</h3>
                                    <button onClick={() => setShowEditInput(false)} className="text-slate-500 hover:text-white"><X className="w-5 h-5" /></button>
                                </div>
                                <textarea 
                                    value={editInstruction}
                                    onChange={(e) => setEditInstruction(e.target.value)}
                                    placeholder="Ex: Remova o braço extra, mude a cor do cabelo para vermelho, corrija os olhos..."
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
                                        Aplicar
                                    </button>
                                </div>
                             </div>
                        </div>
                     )}

                     <img src={generatedResult} alt="Generated Character Sheet" className="w-full h-full object-contain" />
                     
                     <div className="absolute top-4 left-4 bg-black/60 backdrop-blur px-3 py-1 rounded text-xs font-mono text-white flex items-center gap-2 pointer-events-none">
                        <CheckCircle2 className="w-3 h-3 text-green-400" />
                        {mode === 't-pose' ? 'REF RIGGING (1:1)' : mode === 'expression' ? 'EXPRESSÕES & POSES (1:1)' : 'CONCEITO VISUAL (16:9)'}
                     </div>

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
                             <button 
                                onClick={handleDescribeResult}
                                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-full shadow-lg transform hover:scale-105 transition-all flex items-center gap-2 font-bold text-sm"
                            >
                                <ScanEye className="w-4 h-4" /> Obter Prompt
                            </button>
                        </div>
                     )}
                </div>
                
                <div className="w-full bg-slate-800 p-4 rounded-xl border border-slate-700 flex flex-col gap-4 mt-auto">
                    <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
                        <div className="flex-1 w-full">
                            <label className="text-xs text-slate-400 mb-1 block">Nome da Tag do Personagem</label>
                            <input 
                                type="text" 
                                value={newCharName}
                                onChange={(e) => setNewCharName(e.target.value)}
                                placeholder="#MeuNovoPersonagem"
                                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white outline-none focus:border-purple-500"
                            />
                        </div>
                        <div className="flex-1 w-full">
                            <label className="text-xs text-slate-400 mb-1 block">Descrição (Para Consistência)</label>
                            <textarea 
                                value={newCharDescription}
                                onChange={(e) => setNewCharDescription(e.target.value)}
                                placeholder="Descreva as características físicas e roupas para forçar a consistência (ex: cabelo loiro curto, olhos azuis, jaqueta de couro preta)..."
                                className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white outline-none focus:border-purple-500 resize-none h-10 text-sm"
                            />
                        </div>
                        <button 
                            onClick={handleSaveToRoster}
                            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-green-900/20 whitespace-nowrap self-end md:self-center h-10"
                        >
                            <Save className="w-4 h-4" /> Salvar na Lista
                        </button>
                    </div>
                </div>
            </div>
        ) : (
            <div className="text-slate-600 flex flex-col items-center justify-center h-full opacity-60">
                <div className="w-24 h-24 rounded-full bg-slate-800/50 flex items-center justify-center mb-6 border border-slate-700">
                    {mode === 't-pose' ? <Accessibility className="w-10 h-10" /> : mode === 'expression' ? <Smile className="w-10 h-10" /> : <ImageIcon className="w-10 h-10" />}
                </div>
                <p className="text-xl font-medium text-slate-400">Pronto para criar</p>
                <p className="text-sm mt-2 max-w-xs text-center">
                    {mode === 't-pose' 
                        ? "Descreva seu personagem para gerar uma referência de Pose em T estrita adequada para rigging 3D."
                        : mode === 'expression' 
                            ? "Descreva seu personagem para gerar uma folha com múltiplas expressões emocionais e poses de ação dinâmicas."
                            : "Descreva seu personagem para gerar uma folha de arte conceitual com visões de frente, lado e costas."}
                </p>
            </div>
        )}
      </div>
    </div>
  );
};

export default CharacterCreator;