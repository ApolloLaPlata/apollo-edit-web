import React, { useState, useRef, useEffect } from 'react';
import { ApiKey, Character, GenerationSettings } from '../types';
import { enhancePrompt, scriptToPrompts, analyzeStyleFromImage, generateStandaloneMotionPrompt, prepareVeoPromptsWithAI } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Sparkles, BookOpen, Copy, Check, ArrowRight, Eraser, Quote, ScrollText, ScanEye, Upload, X, Film, Layers, UserPlus, Download, Loader2 } from 'lucide-react';
import JSZip from 'jszip';
import CharacterSelector from './CharacterSelector';

interface ScriptRoomProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  characters: Character[];
  globalContext: string;
  settings: GenerationSettings;
}

const ScriptRoom: React.FC<ScriptRoomProps> = ({ apiKeys, setApiKeys, characters, globalContext: initialContext, settings }) => {
  const [activeTab, setActiveTab] = useState<'enhancer' | 'scriptbreaker' | 'style' | 'motion' | 'veo-export'>('enhancer');
  
  // Enhancer State
  const [simplePrompt, setSimplePrompt] = useState('');
  
  // Script Breaker State
  const [narrativeText, setNarrativeText] = useState('');
  const [detectNewCharacters, setDetectNewCharacters] = useState(false);
  
  // Style Detector State
  const [styleImage, setStyleImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Motion Prompter State
  const [staticPrompt, setStaticPrompt] = useState('');
  const [batchProgress, setBatchProgress] = useState('');

  // Shared Output State
  const [outputResult, setOutputResult] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);
  
  // VEO Export State
  const [veoInput, setVeoInput] = useState('');
  const [veoGenerateVideo, setVeoGenerateVideo] = useState(false);
  const [veoInfiniteMode, setVeoInfiniteMode] = useState(true);
  const [veoCharAlias, setVeoCharAlias] = useState<Record<string, { alias: string, imageBase64: string }>>({});
  const [detectedVeoChars, setDetectedVeoChars] = useState<Character[]>([]);

  // Style Context is initialized from props but can be edited here locally
  const [styleContext, setStyleContext] = useState(initialContext || '');

  // UI Feedback
  const [copied, setCopied] = useState(false);

  const apiKeysRef = useRef(apiKeys);
  useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  const handleEnhance = async () => {
      if (!simplePrompt.trim()) return;

      setIsProcessing(true);
      const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));
      const characterContext = selectedCharacters.length > 0 
          ? `\nInclude these characters: ${selectedCharacters.map(c => c.name).join(', ')}` 
          : '';

      try {
          const result = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await enhancePrompt(simplePrompt, styleContext + characterContext, settings, apiKey)
          );
          setOutputResult(result);
      } catch (e: any) {
          toast.error("Erro: " + e.message);
      } finally {
          setIsProcessing(false);
      }
  };

  const handleBreakdown = async () => {
      if (!narrativeText.trim()) return;

      setIsProcessing(true);
      const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));

      try {
          const result = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await scriptToPrompts(narrativeText, styleContext, selectedCharacters, detectNewCharacters, settings, apiKey)
          );
          setOutputResult(result);
      } catch (e: any) {
          toast.error("Erro: " + e.message);
      } finally {
          setIsProcessing(false);
      }
  };

  const handleStyleAnalysis = async () => {
      if (!styleImage) return;

      setIsProcessing(true);
      try {
          const result = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await analyzeStyleFromImage(apiKey, styleImage)
          );
          setOutputResult(result);
      } catch (e: any) {
          toast.error("Erro: " + e.message);
      } finally {
          setIsProcessing(false);
      }
  };

  const handleMotionGen = async () => {
      if (!staticPrompt.trim()) return;

      setIsProcessing(true);
      setBatchProgress('');
      
      // Split input into lines for batch processing
      const lines = staticPrompt.split('\n').filter(line => line.trim().length > 0);
      const results: string[] = [];

      try {
          for (let i = 0; i < lines.length; i++) {
              setBatchProgress(`Processando ${i + 1} de ${lines.length}...`);
              
              // Process individually to ensure high quality per prompt
              const result = await executeWithKeyRotation(
                  apiKeysRef,
                  setApiKeys,
                  async (apiKey) => await generateStandaloneMotionPrompt(lines[i], settings, apiKey)
              );
              
              // Clean result just in case
              const cleanResult = result.replace(/^(Prompt|Motion Prompt):\s*/i, '').trim();
              results.push(cleanResult);
          }
          
          // Join with double newlines for the batch format the user wants
          setOutputResult(results.join('\n\n'));
      } catch (e: any) {
          toast.error("Erro no processamento em lote: " + e.message);
      } finally {
          setIsProcessing(false);
          setBatchProgress('');
      }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const reader = new FileReader();
      reader.onload = (ev) => {
        setStyleImage(ev.target?.result as string);
      };
      reader.readAsDataURL(e.target.files[0]);
    }
  };

  useEffect(() => {
     if (activeTab !== 'veo-export') return;
     // Regex aprimorada para capturar hashtags com acentos e unicode
     const matchHashtags = (veoInput.match(/#[\p{L}\p{N}_-]+/gu) || []).map(t => t.toLowerCase().replace('#', ''));
     const uniqueTags = [...new Set(matchHashtags)];
     const matchedChars = characters.filter(c => {
         // Normaliza personagem (remove estranhos preservando acentos)
         const cNameSanitized = c.name.toLowerCase().replace(/[^\p{L}\p{N}_-]/gu, '');
         const cNameRaw = c.name.toLowerCase().replace('#', '');
         // Found via hashtag exactly, OR found as a text string inside the prompt
         return uniqueTags.includes(cNameSanitized) || uniqueTags.includes(cNameRaw) || veoInput.toLowerCase().includes(cNameRaw);
     });
     
     setDetectedVeoChars(matchedChars);

     setVeoCharAlias(prev => {
        const next = { ...prev };
        matchedChars.forEach((char, idx) => {
            if (!next[char.id]) {
                next[char.id] = {
                    alias: `#Personagem${idx + 1}`,
                    imageBase64: char.previewUrl
                };
            }
        });
        return next;
     });
  }, [veoInput, characters, activeTab]);

  const handleVeoExport = async () => {
    if (!veoInput.trim()) {
        toast.error("Cole os prompts na caixa de texto.");
        return;
    }
    
    setIsProcessing(true);
    const toastId = toast.loading("Reescrevendo e preparando exportação VEO...");
    try {
        const zip = new JSZip();
        
        // 1. Map Characters for the AI
        const characterMap: {name: string, alias: string}[] = [];
        
        detectedVeoChars.forEach(char => {
            const aliasData = veoCharAlias[char.id];
            if (aliasData && aliasData.alias) {
               characterMap.push({ name: char.name, alias: aliasData.alias });
               
               // 2. Prepare images to ZIP
               if (aliasData.imageBase64) {
                   const isPng = aliasData.imageBase64.startsWith("data:image/png");
                   const isWebp = aliasData.imageBase64.startsWith("data:image/webp");
                   const extension = isPng ? 'png' : (isWebp ? 'webp' : 'jpg');
                   const base64Data = aliasData.imageBase64.replace(/^data:image\/\w+;base64,/, "");
                   
                   // Remove caracteres inválidos do alias mas mantem letras e números
                   const cleanAlias = aliasData.alias.replace(/[^a-zA-Z0-9_-]/g, '');
                   const fileName = `${cleanAlias}.${extension}`;
                   zip.file(`imagens_referencia/${fileName}`, base64Data, {base64: true});
               }
            }
        });

        // 3. Pre-alias the input text natively (to guarantee no names slip past Gemini)
        let aliasedInputForAI = veoInput;
        const sortedMap = [...characterMap].sort((a, b) => b.name.length - a.name.length);
        sortedMap.forEach(mapping => {
             // We want to match with or without hashtag, just in case
             const escapedTag = mapping.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
             const regex = new RegExp(`(#${escapedTag}|\\b${escapedTag}\\b)`, 'gi');
             aliasedInputForAI = aliasedInputForAI.replace(regex, mapping.alias);
        });

        // 4. Ask Gemini to write enhanced context and maintain anonymization
        const finalText = await executeWithKeyRotation(
            apiKeysRef,
            setApiKeys,
            async (apiKey) => await prepareVeoPromptsWithAI(aliasedInputForAI, characterMap, settings, veoInfiniteMode, apiKey)
        );

        // 5. Gerar video prompts se solicitado
        if (veoGenerateVideo) {
            const lines = finalText.split('\n').filter(l => l.trim().length > 0);
            const videoPrompts = [];
            toast.loading("Gerando Prompts de Vídeo Animado (Batch)...", { id: toastId });
            for (let i = 0; i < lines.length; i++) {
                const result = await executeWithKeyRotation(
                    apiKeysRef,
                    setApiKeys,
                    async (apiKey) => await generateStandaloneMotionPrompt(lines[i], settings, apiKey)
                );
                videoPrompts.push(result.replace(/^(Prompt|Motion Prompt):\s*/i, '').trim());
            }
            zip.file('prompts_animacao.txt', videoPrompts.join('\n\n'));
        }

        zip.file('prompts.txt', finalText.split('\n').filter(l=>l.trim().length > 0).join('\n\n'));

        // Output Preview na UI
        setOutputResult(finalText);

        const content = await zip.generateAsync({ type: 'blob' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(content);
        a.download = `VEO_Export_Genérico_${new Date().toISOString().split('T')[0]}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        toast.success("Exportação concluída com sucesso!", { id: toastId });
    } catch(e: any) {
        console.error(e);
        toast.error("Erro na exportação: " + e.message, { id: toastId });
    } finally {
        setIsProcessing(false);
    }
  };

  const copyToClipboard = (text: string) => {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
  };

  const toggleCharacter = (id: string) => {
      setSelectedCharacterIds(prev => 
          prev.includes(id) ? prev.filter(cId => cId !== id) : [...prev, id]
      );
  };

  return (
    <div className="h-full flex flex-col md:flex-row gap-6 p-2">
      {/* Left Panel: Tools & Input */}
      <div className="w-full md:w-1/2 bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-6 overflow-y-auto">
        <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2 mb-2">
                <BookOpen className="w-6 h-6 text-purple-400" />
                Sala de Roteiro & Pré-Produção
            </h2>
            <p className="text-sm text-slate-400">
                Ferramentas de IA para transformar ideias, extrair estilos e criar roteiros.
            </p>
        </div>

        {/* Characters */}
        <CharacterSelector 
            characters={characters}
            onSelect={(char) => toggleCharacter(char.id)}
            mode="toggle"
            selectedIds={selectedCharacterIds}
        />

        {/* Tab Switcher Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-2 bg-slate-800 p-2 rounded-lg border border-slate-700">
            <button
                onClick={() => { setActiveTab('enhancer'); setOutputResult(''); }}
                className={`py-2 text-xs font-bold rounded transition-all flex flex-col items-center justify-center gap-1 ${activeTab === 'enhancer' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
            >
                <Sparkles className="w-4 h-4" /> Refinador
            </button>
            <button
                onClick={() => { setActiveTab('scriptbreaker'); setOutputResult(''); }}
                className={`py-2 text-xs font-bold rounded transition-all flex flex-col items-center justify-center gap-1 ${activeTab === 'scriptbreaker' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
            >
                <ScrollText className="w-4 h-4" /> Roteiro
            </button>
            <button
                onClick={() => { setActiveTab('style'); setOutputResult(''); }}
                className={`py-2 text-xs font-bold rounded transition-all flex flex-col items-center justify-center gap-1 ${activeTab === 'style' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
            >
                <ScanEye className="w-4 h-4" /> Estilos
            </button>
             <button
                onClick={() => { setActiveTab('motion'); setOutputResult(''); }}
                className={`py-2 text-xs font-bold rounded transition-all flex flex-col items-center justify-center gap-1 ${activeTab === 'motion' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
            >
                <Film className="w-4 h-4" /> Animador
            </button>
            <button
                onClick={() => { setActiveTab('veo-export'); }}
                className={`py-2 text-xs font-bold rounded transition-all flex flex-col items-center justify-center gap-1 ${activeTab === 'veo-export' ? 'bg-indigo-600 text-white shadow-lg border border-indigo-400' : 'text-slate-400 hover:text-white hover:bg-slate-700 border border-transparent'}`}
                title="Preparar e exportar prompts genéricos para a extensão Auto VEO anti-censura."
            >
                <Download className="w-4 h-4 text-indigo-300" /> Exportar VEO
            </button>
        </div>

        {/* --- CONTENT FOR TABS --- */}

        {activeTab === 'enhancer' && (
            <div className="flex-1 flex flex-col gap-4">
                <div className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex flex-col gap-4 shadow-sm">
                    {/* INPUT 1: Concept */}
                    <div>
                        <label className="text-xs font-bold text-slate-400 uppercase mb-2 flex items-center gap-2">
                             <span className="bg-purple-600 text-white w-5 h-5 rounded-full flex items-center justify-center text-[10px]">1</span>
                             Conceito / Ideia Base
                        </label>
                        <textarea 
                            value={simplePrompt}
                            onChange={(e) => setSimplePrompt(e.target.value)}
                            placeholder="O QUE você quer ver? (Ex: Um cavaleiro lutando contra um dragão na chuva...)"
                            className="w-full h-24 bg-slate-900 border border-slate-600 rounded p-3 text-white resize-none outline-none focus:border-purple-500 text-sm"
                        />
                    </div>
                    {/* INPUT 2: Style */}
                    <div>
                        <label className="text-xs font-bold text-slate-400 uppercase mb-2 flex items-center gap-2">
                             <span className="bg-orange-500 text-white w-5 h-5 rounded-full flex items-center justify-center text-[10px]">2</span>
                             Estilo Visual (Direção de Arte)
                        </label>
                        <textarea
                            value={styleContext}
                            onChange={(e) => setStyleContext(e.target.value)}
                            placeholder="COMO deve parecer? (Ex: Cyberpunk Neon, Fotografia 35mm, Estilo Pixar, Pintura a Óleo...)"
                            className="w-full h-16 bg-slate-900 border border-slate-600 rounded p-3 text-white text-sm outline-none focus:border-orange-500 resize-none"
                        />
                    </div>
                </div>

                <button 
                    onClick={handleEnhance}
                    disabled={isProcessing || !simplePrompt.trim()}
                    className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 disabled:from-slate-700 disabled:to-slate-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-900/50 transition-all"
                >
                    {isProcessing ? <Sparkles className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                    {isProcessing ? "Mesclando & Refinando..." : "Mesclar Estilo & Gerar Prompt"}
                </button>
            </div>
        )}

        {activeTab === 'scriptbreaker' && (
            <div className="flex-1 flex flex-col gap-4">
                <div className="flex-1 flex flex-col">
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-sm font-bold text-slate-300">Texto Narrativo / História</label>
                    </div>
                    <textarea 
                        value={narrativeText}
                        onChange={(e) => setNarrativeText(e.target.value)}
                        placeholder="Cole aqui um parágrafo do seu livro ou roteiro. O Gemini irá detectar seus personagens (Tags) e criar cenas visuais."
                        className="w-full h-48 bg-slate-800 border border-slate-600 rounded p-3 text-white resize-none outline-none focus:ring-2 focus:ring-purple-500 text-sm"
                    />
                </div>

                <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                    <label className="text-xs font-bold text-slate-400 uppercase mb-2 block">Estilo Visual para as Cenas</label>
                    <input 
                        value={styleContext}
                        onChange={(e) => setStyleContext(e.target.value)}
                        placeholder="Ex: Fantasia Sombria, Cyberpunk, Pixar..."
                        className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white text-sm outline-none focus:border-purple-500"
                    />
                </div>
                
                <div 
                    onClick={() => setDetectNewCharacters(!detectNewCharacters)}
                    className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors select-none ${detectNewCharacters ? 'bg-purple-900/20 border-purple-500/50' : 'bg-slate-800 border-slate-700 hover:bg-slate-750'}`}
                >
                    <div className={`w-5 h-5 rounded border flex items-center justify-center ${detectNewCharacters ? 'bg-purple-600 border-purple-500' : 'border-slate-500'}`}>
                        {detectNewCharacters && <Check className="w-3 h-3 text-white" />}
                    </div>
                    <div>
                        <span className={`text-sm font-bold block ${detectNewCharacters ? 'text-purple-300' : 'text-slate-300'}`}>Detectar e Criar Personagens</span>
                        <span className="text-xs text-slate-500 block">Se marcado, a IA também gerará prompts descritivos para novos personagens encontrados no texto, útil para o Laboratório.</span>
                    </div>
                </div>

                <button 
                    onClick={handleBreakdown}
                    disabled={isProcessing || !narrativeText.trim()}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-900/50 transition-all"
                >
                    {isProcessing ? <ScrollText className="w-5 h-5 animate-pulse" /> : (detectNewCharacters ? <UserPlus className="w-5 h-5" /> : <ArrowRight className="w-5 h-5" />)}
                    {isProcessing ? "Analisando História..." : (detectNewCharacters ? "Analisar Personagens & Cenas" : "Converter em Lista de Prompts")}
                </button>
            </div>
        )}

        {activeTab === 'style' && (
            <div className="flex-1 flex flex-col gap-4">
                <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-sm text-slate-400">
                    Faça upload de uma imagem (anime, filme, pintura) para extrair <strong>apenas</strong> a direção de arte e estilo visual, ignorando os personagens.
                </div>
                
                <div 
                    onClick={() => fileInputRef.current?.click()}
                    className="border-2 border-dashed border-slate-700 rounded-lg p-6 cursor-pointer hover:bg-slate-800 transition-colors flex flex-col items-center justify-center min-h-[200px]"
                >
                    {styleImage ? (
                        <div className="relative w-full h-48">
                            <img src={styleImage} alt="Ref" className="w-full h-full object-contain rounded" />
                            <button 
                                onClick={(e) => { e.stopPropagation(); setStyleImage(null); }}
                                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-lg hover:bg-red-600"
                            >
                                <X className="w-3 h-3" />
                            </button>
                        </div>
                    ) : (
                        <div className="text-center text-slate-500">
                            <Upload className="w-10 h-10 mx-auto mb-2 text-purple-500" />
                            <span className="font-bold">Upload Imagem de Estilo</span>
                        </div>
                    )}
                    <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                </div>

                <button 
                    onClick={handleStyleAnalysis}
                    disabled={isProcessing || !styleImage}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-900/50 transition-all"
                >
                    {isProcessing ? <ScanEye className="w-5 h-5 animate-pulse" /> : <ScanEye className="w-5 h-5" />}
                    {isProcessing ? "Analisando Estilo..." : "Extrair Estilo Visual"}
                </button>
            </div>
        )}

        {activeTab === 'motion' && (
             <div className="flex-1 flex flex-col gap-4">
                 <div className="p-4 bg-slate-800/50 rounded-lg border border-slate-700 text-sm text-slate-400">
                    <strong>Batch Converter (Lote):</strong> Cole uma lista de prompts de imagem (um por linha). A IA gerará a lista formatada de prompts de vídeo, pronta para exportar.
                </div>
                <div className="flex-1 flex flex-col">
                    <label className="text-sm font-bold text-slate-300 mb-2">Lista de Prompts (Img) - Um por linha</label>
                    <textarea 
                        value={staticPrompt}
                        onChange={(e) => setStaticPrompt(e.target.value)}
                        placeholder={`#Heroi olhando para o horizonte\n#Heroi correndo na chuva\nCarro futurista voando`}
                        className="w-full h-48 bg-slate-800 border border-slate-600 rounded p-3 text-white resize-none outline-none focus:ring-2 focus:ring-purple-500 text-xs font-mono"
                    />
                </div>
                <button 
                    onClick={handleMotionGen}
                    disabled={isProcessing || !staticPrompt.trim()}
                    className="w-full bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 text-white py-3 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-purple-900/50 transition-all"
                >
                    {isProcessing ? <Film className="w-5 h-5 animate-spin" /> : <Layers className="w-5 h-5" />}
                    {isProcessing ? (batchProgress || "Processando...") : "Gerar Lote de Animação"}
                </button>
            </div>
        )}

        {activeTab === 'veo-export' && (
             <div className="flex-1 flex flex-col gap-4">
                 <div className="p-4 bg-indigo-900/20 rounded-lg border border-indigo-500/30 text-sm text-indigo-200">
                    <strong>Exportador Auto VEO:</strong> Insira seus prompts. A IA substituirá os nomes reais por nomes genéricos (ex: <code>#Personagem1</code>) e gerará um ZIP pronto para a extensão, reduzindo as chances de censura!
                </div>
                <div className="flex-1 flex flex-col">
                    <label className="text-sm font-bold text-slate-300 mb-2">Lista de Prompts Brutos</label>
                    <textarea 
                        value={veoInput}
                        onChange={(e) => setVeoInput(e.target.value)}
                        placeholder={`#Lula num debate acalorado\n[CONTINUA] Ele aponta o dedo para a câmera`}
                        className="w-full h-32 bg-slate-800 border border-slate-600 rounded p-3 text-white resize-none outline-none focus:ring-2 focus:ring-indigo-500 text-xs font-mono"
                        disabled={isProcessing}
                    />
                </div>

                {detectedVeoChars.length > 0 ? (
                    <div className="bg-slate-800 p-3 rounded-lg border border-slate-700">
                        <label className="text-xs font-bold text-slate-400 uppercase mb-2 block">Seleção de Referências e Máscara</label>
                        <div className="flex flex-col gap-2">
                        {detectedVeoChars.map(char => {
                            const data = veoCharAlias[char.id];
                            if (!data) return null;
                            return (
                                <div key={char.id} className="flex items-center gap-3 bg-slate-900 p-2 rounded border border-slate-700">
                                    <div className="w-10 h-10 rounded overflow-hidden shrink-0">
                                        <img src={data.imageBase64 || char.previewUrl} alt={char.name} className="w-full h-full object-cover" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold text-white truncate">{char.name}</p>
                                        <input 
                                            value={data.alias}
                                            onChange={(e) => {
                                                setVeoCharAlias(prev => ({
                                                    ...prev,
                                                    [char.id]: { ...data, alias: e.target.value }
                                                }))
                                            }}
                                            className="bg-slate-800 border border-slate-600 rounded px-2 py-1 text-xs text-indigo-300 w-full mt-1 outline-none focus:border-indigo-500 font-mono"
                                        />
                                    </div>
                                    <div className="shrink-0 flex flex-col items-end">
                                        <label className="text-[10px] text-slate-500 mb-1">Referência (Capa/Sheet):</label>
                                        <select
                                           className="bg-slate-800 text-xs text-white border border-slate-600 rounded py-1 px-2 outline-none max-w-[120px]"
                                           value={data.imageBase64}
                                           onChange={(e) => {
                                               setVeoCharAlias(prev => ({
                                                    ...prev,
                                                    [char.id]: { ...data, imageBase64: e.target.value }
                                                }))
                                           }}
                                        >   
                                            <option value={char.previewUrl}>Capa</option>
                                            {char.images.map((img, i) => (
                                                <option key={i} value={img}>Foto {i+1}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>
                            );
                        })}
                        </div>
                    </div>
                ) : (
                    <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-700/50 flex flex-col items-center text-center">
                        <ScanEye className="w-6 h-6 text-slate-500 mb-2 opacity-50" />
                        <span className="text-sm text-slate-400 font-bold">Nenhum personagem detectado no Roteiro.</span>
                        <span className="text-xs text-slate-500 mt-1">Para abrir o Menu de Seleção de Foto (Capa/Character Sheet) e Máscara, escreva a hashtag exata do personagem no roteiro acima. Exemplo: Se o nome for "Charlinho", digite `#Charlinho`.</span>
                    </div>
                )}
                
                <div className="grid grid-cols-2 gap-3">
                    <div 
                        onClick={() => !isProcessing && setVeoGenerateVideo(!veoGenerateVideo)}
                        className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors select-none ${veoGenerateVideo ? 'bg-indigo-900/20 border-indigo-500/50' : 'bg-slate-800 border-slate-700 hover:bg-slate-750'}`}
                    >
                        <div className={`w-5 h-5 shrink-0 rounded border flex items-center justify-center ${veoGenerateVideo ? 'bg-indigo-600 border-indigo-500' : 'border-slate-500'}`}>
                            {veoGenerateVideo && <Check className="w-3 h-3 text-white" />}
                        </div>
                        <div>
                            <span className={`text-xs font-bold block ${veoGenerateVideo ? 'text-indigo-300' : 'text-slate-300'}`}>Vídeo (Runway/Veo)</span>
                            <span className="text-[10px] text-slate-500 block leading-tight">Gerar prompts de animação extras.</span>
                        </div>
                    </div>

                    <div 
                        onClick={() => !isProcessing && setVeoInfiniteMode(!veoInfiniteMode)}
                        className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors select-none ${veoInfiniteMode ? 'bg-indigo-900/20 border-indigo-500/50' : 'bg-slate-800 border-slate-700 hover:bg-slate-750'}`}
                    >
                        <div className={`w-5 h-5 shrink-0 rounded border flex items-center justify-center ${veoInfiniteMode ? 'bg-indigo-600 border-indigo-500' : 'border-slate-500'}`}>
                            {veoInfiniteMode && <Check className="w-3 h-3 text-white" />}
                        </div>
                        <div>
                            <span className={`text-xs font-bold block ${veoInfiniteMode ? 'text-indigo-300' : 'text-slate-300'}`}>Vídeo Infinito (Semântica)</span>
                            <span className="text-[10px] text-slate-500 block leading-tight">Forçar prefixos [CONTINUA] ou [CORTE].</span>
                        </div>
                    </div>
                </div>

                <div className="flex gap-2 mt-2">
                    <button 
                        onClick={() => {
                            if (outputResult) setVeoInput(outputResult);
                        }}
                        disabled={isProcessing || !outputResult}
                        className="bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 text-white py-2 px-3 rounded-lg font-bold flex items-center justify-center gap-2 transition-all flex-1 text-xs"
                    >
                         Puxar Resultado
                    </button>
                    
                    <button 
                        onClick={handleVeoExport}
                        disabled={isProcessing || !veoInput.trim()}
                        className="flex-[2] bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 text-white py-2 rounded-lg font-bold flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/50 transition-all text-sm"
                    >
                        {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
                        {isProcessing ? "Gerando..." : "Baixar ZIP + Prompts"}
                    </button>
                </div>
            </div>
        )}

      </div>

      {/* Right Panel: Output */}
      <div className="w-full md:w-1/2 bg-slate-900 rounded-xl border border-slate-700 p-6 flex flex-col gap-4">
            <div className="flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Quote className="w-5 h-5 text-slate-400" /> Resultado Gerado
                </h3>
                {(outputResult) && (
                    <div className="flex gap-2">
                         <button 
                            onClick={() => setOutputResult('')}
                            className="p-2 text-slate-500 hover:text-red-400 transition-colors"
                            title="Limpar"
                        >
                            <Eraser className="w-4 h-4" />
                        </button>
                        <button 
                            onClick={() => copyToClipboard(outputResult)}
                            className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs font-bold flex items-center gap-2 transition-colors"
                        >
                            {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
                            {copied ? "Copiado!" : "Copiar Texto"}
                        </button>
                    </div>
                )}
            </div>

            <div className="flex-1 bg-black/30 rounded-lg border border-slate-800 p-4 relative font-mono text-sm text-slate-300 overflow-y-auto">
                {outputResult ? (
                    <p className="whitespace-pre-wrap">{outputResult}</p>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 italic gap-2 text-center p-4">
                        {activeTab === 'enhancer' && <Sparkles className="w-8 h-8 opacity-20" />}
                        {activeTab === 'scriptbreaker' && <ScrollText className="w-8 h-8 opacity-20" />}
                        {activeTab === 'style' && <ScanEye className="w-8 h-8 opacity-20" />}
                        {activeTab === 'motion' && <Film className="w-8 h-8 opacity-20" />}
                        
                        <span>
                            {activeTab === 'enhancer' && "O prompt refinado (Conceito + Estilo) aparecerá aqui."}
                            {activeTab === 'scriptbreaker' && "A lista de cenas aparecerá aqui."}
                            {activeTab === 'style' && "A descrição do estilo visual aparecerá aqui. Copie e cole em 'Configurações do Diretor' na aba Auto Execução."}
                            {activeTab === 'motion' && "Cole seus prompts de imagem (um por linha) à esquerda. A lista formatada de prompts de vídeo aparecerá aqui, pronta para copiar e colar."}
                        </span>
                    </div>
                )}
            </div>
            
            <div className="p-3 bg-purple-900/20 border border-purple-500/30 rounded text-xs text-purple-200 flex gap-2">
                <div className="mt-0.5"><Copy className="w-3 h-3" /></div>
                <div>
                    <strong>Dica de Fluxo de Trabalho:</strong> Copie o resultado e cole na área correspondente da aba <span className="font-bold text-white">Auto Execução</span>.
                    {activeTab === 'style' && " (Cole no campo 'Estilo Visual')."}
                </div>
            </div>
      </div>
    </div>
  );
};

export default ScriptRoom;