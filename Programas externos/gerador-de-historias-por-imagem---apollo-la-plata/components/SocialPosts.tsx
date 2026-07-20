import React, { useState, useRef } from 'react';
import { ApiKey, GeneratedImage, GenerationSettings, Character } from '../types';
import { generateSocialPost } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Image as ImageIcon, Type, Layers, Download, Loader2, X, Zap, Palette, MessageSquare, Wand2, Copy } from 'lucide-react';
import { MODELS } from '../constants';
import CharacterSelector from './CharacterSelector';

interface SocialPostsProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  addGeneratedImage: (img: GeneratedImage) => void;
  characters: Character[];
  settings?: GenerationSettings;
  onImageClick?: (image: GeneratedImage) => void;
}

const SocialPosts: React.FC<SocialPostsProps> = ({ apiKeys, setApiKeys, addGeneratedImage, characters, settings, onImageClick }) => {
  // Model Selector (Default to Flash 2.5)
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');

  // Inputs
  const [postContext, setPostContext] = useState('');
  const [overlayText, setOverlayText] = useState('');
  const [stylePrompt, setStylePrompt] = useState('Fotografia realista, alta qualidade, iluminação de estúdio');
  const [aspectRatio, setAspectRatio] = useState<'1:1' | '4:5' | '16:9' | '9:16'>('1:1');
  
  // Character Selection
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);

  // Reference Image
  const [referenceImage, setReferenceImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Processing
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedResult, setGeneratedResult] = useState<GeneratedImage | null>(null);

  const apiKeysRef = useRef(apiKeys);
  React.useEffect(() => { apiKeysRef.current = apiKeys; }, [apiKeys]);

  const toggleCharacter = (id: string) => {
      setSelectedCharacterIds(prev => 
          prev.includes(id) ? prev.filter(cId => cId !== id) : [...prev, id]
      );
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
          const reader = new FileReader();
          reader.onload = (event) => {
              setReferenceImage(event.target?.result as string);
          };
          reader.readAsDataURL(e.target.files[0]);
      }
  };

  const handleGenerate = async () => {
      if (!postContext.trim()) {
          toast.error("Insira o contexto da postagem.");
          return;
      }

      setIsGenerating(true);
      
      const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));
      
      try {
          const imageUrl = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => await generateSocialPost(apiKey, {
                  postContext,
                  overlayText,
                  characters: selectedCharacters,
                  stylePrompt,
                  aspectRatio,
                  modelId: selectedModel,
                  referenceImage,
                  brandKit: settings?.brandKit
              })
          );

          const promptLabel = `[Postagem] ${postContext.slice(0, 30)}...`;

          // Save to Gallery
          const galleryItem: GeneratedImage = {
              id: crypto.randomUUID(),
              prompt: promptLabel,
              imageUrl: imageUrl,
              timestamp: Date.now(),
              characterIds: selectedCharacterIds,
              aspectRatio: aspectRatio
          };
          
          setGeneratedResult(galleryItem);
          addGeneratedImage(galleryItem);

      } catch (e: any) {
          toast.error("Erro: " + e.message);
      } finally {
          setIsGenerating(false);
      }
  };

  const handleDownload = () => {
    if (!generatedResult) return;
    const a = document.createElement('a');
    a.href = generatedResult.imageUrl;
    a.download = `postagem-${Date.now()}.png`;
    a.click();
  };

  const [caption, setCaption] = useState('');
  const [isGeneratingCaption, setIsGeneratingCaption] = useState(false);

  const handleGenerateCaption = async () => {
      if (!postContext.trim()) {
          toast.error("Descreva o contexto da postagem primeiro.");
          return;
      }

      setIsGeneratingCaption(true);
      try {
          const prompt = `
              Crie uma legenda (copy) para um post de Instagram/LinkedIn sobre o seguinte contexto: "${postContext}".
              O texto de destaque na imagem é: "${overlayText}".
              
              A legenda deve ser engajadora, ter uma chamada para ação (CTA) no final e incluir de 3 a 5 hashtags relevantes.
          `;

          const result = await executeWithKeyRotation(
              apiKeysRef,
              setApiKeys,
              async (apiKey) => {
                  const { GoogleGenAI } = await import('@google/genai');
                  const ai = new GoogleGenAI({ apiKey });
                  const response = await ai.models.generateContent({
                      model: 'gemini-3.1-flash-lite-preview',
                      contents: prompt,
                  });
                  return response.text;
              }
          );

          if (result) {
              setCaption(result);
              toast.success("Legenda gerada!");
          }
      } catch (error: any) {
          console.error("Erro ao gerar legenda:", error);
          toast.error("Erro ao gerar legenda: " + error.message);
      } finally {
          setIsGeneratingCaption(false);
      }
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-6 p-6 overflow-hidden">
      {/* Left Panel - Controls */}
      <div className="w-full lg:w-[450px] flex-shrink-0 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar pb-20 lg:pb-0">
        
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center text-emerald-400">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Postagens Sociais</h2>
              <p className="text-sm text-slate-400">Crie imagens para redes sociais com texto</p>
            </div>
          </div>

          <div className="space-y-5">
            {/* Model Selection */}
            <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                    <Wand2 className="w-4 h-4 text-emerald-400" />
                    Modelo de IA
                </label>
                <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                >
                    {MODELS.map(model => (
                        <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                </select>
                <p className="text-xs text-slate-500">Imagen 3 ou Flash Image são recomendados para renderização de texto.</p>
            </div>

            {/* Aspect Ratio */}
            <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-emerald-400" />
                    Formato (Proporção)
                </label>
                <div className="grid grid-cols-4 gap-2">
                    {[
                        { id: '1:1', label: 'Quadrado', icon: '1:1' },
                        { id: '4:5', label: 'Feed IG', icon: '4:5' },
                        { id: '16:9', label: 'Paisagem', icon: '16:9' },
                        { id: '9:16', label: 'Stories', icon: '9:16' }
                    ].map(ratio => (
                        <button
                            key={ratio.id}
                            onClick={() => setAspectRatio(ratio.id as any)}
                            className={`py-2 px-1 rounded-lg border text-xs font-medium transition-all ${
                                aspectRatio === ratio.id 
                                ? 'bg-emerald-600/20 border-emerald-500 text-emerald-400' 
                                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
                            }`}
                        >
                            {ratio.icon}
                        </button>
                    ))}
                </div>
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

            {/* Post Context */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-emerald-400" />
                Contexto da Postagem
              </label>
              <textarea
                value={postContext}
                onChange={(e) => setPostContext(e.target.value)}
                placeholder="Ex: O personagem comentando sobre inteligência artificial, segurando um smartphone com cara de surpreso..."
                className="w-full h-24 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 resize-none"
              />
            </div>

            {/* Reference Image */}
            <div className="space-y-2">
                <div className="flex justify-between items-end">
                    <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                        <ImageIcon className="w-4 h-4 text-emerald-400" />
                        Imagem de Referência (Cenário/Objeto)
                    </label>
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
                                className="absolute top-2 right-2 bg-red-500 text-white p-1 rounded-full hover:bg-red-600"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    ) : (
                        <div className="text-center">
                            <ImageIcon className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                            <p className="text-sm text-slate-400">Clique para enviar uma imagem de referência</p>
                            <p className="text-xs text-slate-500 mt-1">Ex: Foto do Rio de Janeiro, um produto específico, etc.</p>
                        </div>
                    )}
                </div>
                <input 
                    type="file" 
                    ref={fileInputRef} 
                    onChange={handleImageUpload} 
                    accept="image/*" 
                    className="hidden" 
                />
            </div>

            {/* Overlay Text */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Type className="w-4 h-4 text-emerald-400" />
                Texto na Imagem (Opcional)
              </label>
              <input
                type="text"
                value={overlayText}
                onChange={(e) => setOverlayText(e.target.value)}
                placeholder="Ex: NOVIDADE NA ÁREA!"
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
              <p className="text-xs text-slate-500">O texto será renderizado dentro da imagem pela IA.</p>
            </div>

            {/* Style */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Palette className="w-4 h-4 text-emerald-400" />
                Estilo Visual
              </label>
              <input
                type="text"
                value={stylePrompt}
                onChange={(e) => setStylePrompt(e.target.value)}
                placeholder="Ex: Fotografia realista, iluminação dramática..."
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !postContext.trim()}
              className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-emerald-900/50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  Gerando Postagem...
                </>
              ) : (
                <>
                  <Zap className="w-6 h-6" />
                  Gerar Postagem
                </>
              )}
            </button>

            {/* Caption Generation */}
            <div className="pt-4 border-t border-slate-800 space-y-4">
                <button
                    onClick={handleGenerateCaption}
                    disabled={isGeneratingCaption || !postContext.trim()}
                    className="w-full py-2 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-900 disabled:text-slate-600 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 border border-slate-700"
                >
                    {isGeneratingCaption ? (
                        <><Loader2 className="w-4 h-4 animate-spin" /> Gerando Legenda...</>
                    ) : (
                        <><MessageSquare className="w-4 h-4" /> Gerar Legenda (Copy)</>
                    )}
                </button>

                {caption && (
                    <div className="space-y-2">
                        <label className="text-xs font-bold text-slate-400 uppercase flex justify-between items-center">
                            <span>Legenda Gerada</span>
                            <button 
                                onClick={() => { navigator.clipboard.writeText(caption); toast.success("Copiado!"); }}
                                className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                            >
                                <Copy className="w-3 h-3" /> Copiar
                            </button>
                        </label>
                        <textarea
                            value={caption}
                            onChange={(e) => setCaption(e.target.value)}
                            className="w-full h-40 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-emerald-500 resize-none custom-scrollbar"
                        />
                    </div>
                )}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Preview */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col relative">
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-900/50 backdrop-blur-sm z-10">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-emerald-400" />
            Resultado
          </h3>
          {generatedResult && (
            <div className="flex gap-2">
              <button
                onClick={handleDownload}
                className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors"
                title="Baixar Imagem"
              >
                <Download className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>

        <div className="flex-1 p-6 flex items-center justify-center bg-slate-950 overflow-y-auto">
          {isGenerating ? (
            <div className="flex flex-col items-center gap-4 text-emerald-400">
              <Loader2 className="w-12 h-12 animate-spin" />
              <p className="font-medium animate-pulse">Criando postagem com texto...</p>
            </div>
          ) : generatedResult ? (
            <div className="relative group max-w-full max-h-full flex items-center justify-center">
              <img 
                src={generatedResult.imageUrl} 
                alt="Generated Post" 
                className="max-w-full max-h-full object-contain rounded-lg shadow-2xl cursor-pointer"
                onClick={() => onImageClick && onImageClick(generatedResult)}
              />
            </div>
          ) : (
            <div className="text-center text-slate-500 flex flex-col items-center gap-3">
              <MessageSquare className="w-16 h-16 opacity-20" />
              <p>Preencha o contexto e clique em Gerar para criar uma postagem.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SocialPosts;
