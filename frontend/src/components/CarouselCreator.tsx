import React, { useState } from 'react';
import { ApiKey, GeneratedImage, GenerationSettings, Character } from '../types';
import { generateSocialPost } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';
import toast from 'react-hot-toast';
import { Layers, Loader2, Wand2, Plus, Trash2, GripVertical, Image as ImageIcon, Sparkles, Copy, MessageSquare } from 'lucide-react';
import { MODELS } from '../constants';
import CharacterSelector from './CharacterSelector';

interface CarouselCreatorProps {
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
  addGeneratedImage: (img: GeneratedImage) => void;
  characters: Character[];
  settings?: GenerationSettings;
  onImageClick?: (image: GeneratedImage) => void;
}

interface Slide {
    id: string;
    prompt: string;
    overlayText: string;
    status: 'idle' | 'generating' | 'done' | 'error';
    imageUrl?: string;
    error?: string;
}

const CarouselCreator: React.FC<CarouselCreatorProps> = ({ apiKeys, setApiKeys, addGeneratedImage, characters, settings, onImageClick }) => {
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash-image');
  const [topic, setTopic] = useState('');
  const [slideCount, setSlideCount] = useState(5);
  const [slides, setSlides] = useState<Slide[]>([]);
  const [selectedCharacterIds, setSelectedCharacterIds] = useState<string[]>([]);
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [isGeneratingImages, setIsGeneratingImages] = useState(false);

  const toggleCharacter = (id: string) => {
      setSelectedCharacterIds(prev => 
          prev.includes(id) ? prev.filter(cId => cId !== id) : [...prev, id]
      );
  };

  const handleGenerateScript = async () => {
      if (!topic.trim()) {
          toast.error("Por favor, insira um tópico para o carrossel.");
          return;
      }

      setIsGeneratingScript(true);
      try {
          const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));
          const charContext = selectedCharacters.length > 0 
              ? `Personagens a incluir: ${selectedCharacters.map(c => c.name).join(', ')}` 
              : '';

          const brandKitContext = settings?.brandKit ? `
              Diretrizes da Marca (Brand Kit):
              - Cores: ${settings.brandKit.colors.join(', ')}
              - Fonte: ${settings.brandKit.fontFamily || 'Padrão'}
              Certifique-se de que as descrições visuais (prompts) incorporem essas cores de forma natural na cena (ex: roupas, iluminação, objetos de fundo).
          ` : '';

          const prompt = `
              Crie um roteiro para um carrossel de Instagram/LinkedIn com exatamente ${slideCount} slides sobre o seguinte tópico: "${topic}".
              ${charContext}
              ${brandKitContext}
              
              Retorne APENAS um array JSON válido. Cada objeto no array deve representar um slide e conter:
              - "prompt": A descrição visual detalhada da imagem para a IA gerar.
              - "overlayText": O texto curto e chamativo que será escrito por cima da imagem.
              
              Exemplo de saída:
              [
                  { "prompt": "Um homem de terno sorrindo e apontando para um gráfico de crescimento, fundo de escritório moderno, iluminação cinematográfica", "overlayText": "Como dobrar suas vendas em 30 dias" },
                  { "prompt": "Close-up de mãos digitando em um notebook, luz suave entrando pela janela", "overlayText": "Passo 1: Otimize seu perfil" }
              ]
          `;

          const result = await executeWithKeyRotation(
              { current: apiKeys },
              setApiKeys,
              async (apiKey) => {
                  const { GoogleGenAI } = await import('@google/genai');
                  const ai = new GoogleGenAI({ apiKey });
                  const response = await ai.models.generateContent({
                      model: 'gemini-3.1-flash-lite-preview',
                      contents: prompt,
                      config: {
                          responseMimeType: "application/json",
                      }
                  });
                  return response.text;
              }
          );

          if (result) {
              const parsedSlides = JSON.parse(result);
              setSlides(parsedSlides.map((s: any) => ({
                  id: crypto.randomUUID(),
                  prompt: s.prompt,
                  overlayText: s.overlayText,
                  status: 'idle'
              })));
              toast.success("Roteiro do carrossel gerado!");
          }
      } catch (error: any) {
          console.error("Erro ao gerar roteiro:", error);
          toast.error("Erro ao gerar roteiro: " + error.message);
      } finally {
          setIsGeneratingScript(false);
      }
  };

  const handleAddSlide = () => {
      setSlides([...slides, { id: crypto.randomUUID(), prompt: '', overlayText: '', status: 'idle' }]);
  };

  const handleRemoveSlide = (id: string) => {
      setSlides(slides.filter(s => s.id !== id));
  };

  const handleSlideChange = (id: string, field: 'prompt' | 'overlayText', value: string) => {
      setSlides(slides.map(s => s.id === id ? { ...s, [field]: value } : s));
  };

  const moveSlide = (dragIndex: number, hoverIndex: number) => {
      const draggedSlide = slides[dragIndex];
      const newSlides = [...slides];
      newSlides.splice(dragIndex, 1);
      newSlides.splice(hoverIndex, 0, draggedSlide);
      setSlides(newSlides);
  };

  const [draggedIndex, setDraggedIndex] = useState<number | null>(null);

  const [caption, setCaption] = useState('');
  const [isGeneratingCaption, setIsGeneratingCaption] = useState(false);

  const handleGenerateCaption = async () => {
      if (slides.length === 0 || !topic.trim()) {
          toast.error("Gere um roteiro primeiro.");
          return;
      }

      setIsGeneratingCaption(true);
      try {
          const prompt = `
              Crie uma legenda (copy) para um carrossel de Instagram/LinkedIn sobre o tópico: "${topic}".
              O carrossel tem ${slides.length} slides com os seguintes textos de destaque:
              ${slides.map((s, i) => `Slide ${i+1}: ${s.overlayText}`).join('\n')}
              
              A legenda deve ser engajadora, ter uma chamada para ação (CTA) no final e incluir de 3 a 5 hashtags relevantes.
          `;

          const result = await executeWithKeyRotation(
              { current: apiKeys },
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

  const handleGenerateAllImages = async () => {
      if (slides.length === 0) return;
      
      setIsGeneratingImages(true);
      
      const activeKeys = apiKeys.filter(k => k.isActive);
      if (activeKeys.length === 0) {
          toast.error("Nenhuma chave de API ativa.");
          setIsGeneratingImages(false);
          return;
      }

      const selectedCharacters = characters.filter(c => selectedCharacterIds.includes(c.id));

      for (let i = 0; i < slides.length; i++) {
          const slide = slides[i];
          if (slide.status === 'done' && slide.imageUrl) continue; // Skip already generated

          setSlides(prev => prev.map(s => s.id === slide.id ? { ...s, status: 'generating' } : s));

          try {
              const imageUrl = await executeWithKeyRotation(
                  { current: apiKeys },
                  setApiKeys,
                  async (apiKey) => await generateSocialPost(apiKey, {
                      postContext: slide.prompt,
                      overlayText: slide.overlayText,
                      characters: selectedCharacters,
                      stylePrompt: settings?.globalContext || '',
                      aspectRatio: '1:1', // Standard carousel size
                      modelId: selectedModel,
                      brandKit: settings?.brandKit
                  })
              );

              const newImage: GeneratedImage = {
                  id: crypto.randomUUID(),
                  prompt: `[Carrossel Slide ${i+1}] ${slide.prompt}`,
                  imageUrl: imageUrl,
                  timestamp: Date.now(),
                  category: 'social',
                  model: selectedModel,
                  settings: settings
              };

              addGeneratedImage(newImage);

              setSlides(prev => prev.map(s => s.id === slide.id ? { ...s, status: 'done', imageUrl: imageUrl } : s));
          } catch (error: any) {
              setSlides(prev => prev.map(s => s.id === slide.id ? { ...s, status: 'error', error: error.message } : s));
              toast.error(`Erro no slide ${i+1}: ${error.message}`);
          }
      }

      setIsGeneratingImages(false);
      toast.success("Geração de carrossel concluída!");
  };

  return (
    <div className="h-full flex flex-col lg:flex-row gap-6 p-6 overflow-hidden">
      {/* Left Panel - Controls */}
      <div className="w-full lg:w-[400px] flex-shrink-0 flex flex-col gap-6 overflow-y-auto pr-2 custom-scrollbar pb-20 lg:pb-0">
        
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/20 flex items-center justify-center text-indigo-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Criador de Carrossel</h2>
              <p className="text-sm text-slate-400">Gere posts em sequência (1:1)</p>
            </div>
          </div>

          <div className="space-y-5">
            {/* Model Selection */}
            <div className="space-y-2">
                <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                    <Wand2 className="w-4 h-4 text-indigo-400" />
                    Modelo de IA
                </label>
                <select 
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500"
                >
                    {MODELS.map(m => (
                        <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                </select>
            </div>

            {/* Characters */}
            {characters.length === 0 ? (
                <div className="text-sm text-slate-500 italic bg-slate-950 p-3 rounded-lg border border-slate-800">
                    Nenhum personagem cadastrado.
                </div>
            ) : (
                <CharacterSelector 
                    characters={characters}
                    onSelect={(char) => toggleCharacter(char.id)}
                    mode="toggle"
                    selectedIds={selectedCharacterIds}
                    label="Personagens do Carrossel"
                />
            )}

            {/* Topic Input */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300 flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                Tópico do Carrossel
              </label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Ex: 5 dicas para melhorar a produtividade no home office..."
                className="w-full h-24 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 resize-none"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-300">Número de Slides: {slideCount}</label>
              <input 
                type="range" 
                min="2" 
                max="10" 
                value={slideCount} 
                onChange={(e) => setSlideCount(parseInt(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>

            <button
              onClick={handleGenerateScript}
              disabled={isGeneratingScript || !topic.trim()}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-800 disabled:text-slate-500 text-white font-bold rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-indigo-900/20"
            >
              {isGeneratingScript ? (
                <><Loader2 className="w-5 h-5 animate-spin" /> Criando Roteiro...</>
              ) : (
                <><Sparkles className="w-5 h-5" /> Gerar Roteiro do Carrossel</>
              )}
            </button>

            {/* Caption Generation */}
            <div className="pt-4 border-t border-slate-800 space-y-4">
                <button
                    onClick={handleGenerateCaption}
                    disabled={isGeneratingCaption || slides.length === 0}
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
                                className="text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                            >
                                <Copy className="w-3 h-3" /> Copiar
                            </button>
                        </label>
                        <textarea
                            value={caption}
                            onChange={(e) => setCaption(e.target.value)}
                            className="w-full h-40 bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-300 text-sm focus:outline-none focus:border-indigo-500 resize-none custom-scrollbar"
                        />
                    </div>
                )}
            </div>
          </div>
        </div>
      </div>

      {/* Right Panel - Slides Editor */}
      <div className="flex-1 bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col overflow-hidden shadow-xl relative">
        <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Layers className="w-5 h-5 text-indigo-400" />
                Slides do Carrossel ({slides.length})
            </h3>
            <div className="flex gap-2">
                <button
                    onClick={handleAddSlide}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white text-sm rounded-lg flex items-center gap-1 transition-colors"
                >
                    <Plus className="w-4 h-4" /> Adicionar Slide
                </button>
                <button
                    onClick={handleGenerateAllImages}
                    disabled={isGeneratingImages || slides.length === 0}
                    className="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-800 disabled:text-slate-500 text-white text-sm font-bold rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-emerald-900/20"
                >
                    {isGeneratingImages ? (
                        <><Loader2 className="w-4 h-4 animate-spin" /> Gerando...</>
                    ) : (
                        <><ImageIcon className="w-4 h-4" /> Gerar Todas as Imagens</>
                    )}
                </button>
            </div>
        </div>

        <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-4">
            {slides.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 space-y-4">
                    <Layers className="w-16 h-16 opacity-20" />
                    <p>Descreva um tópico e clique em "Gerar Roteiro" para começar.</p>
                </div>
            ) : (
                slides.map((slide, index) => (
                    <div 
                        key={slide.id} 
                        draggable
                        onDragStart={(e) => {
                            setDraggedIndex(index);
                            e.dataTransfer.effectAllowed = 'move';
                            // Optional: set drag image
                        }}
                        onDragOver={(e) => {
                            e.preventDefault();
                            e.dataTransfer.dropEffect = 'move';
                        }}
                        onDrop={(e) => {
                            e.preventDefault();
                            if (draggedIndex !== null && draggedIndex !== index) {
                                moveSlide(draggedIndex, index);
                            }
                            setDraggedIndex(null);
                        }}
                        className={`bg-slate-950 border ${slide.status === 'done' ? 'border-emerald-500/50' : slide.status === 'error' ? 'border-red-500/50' : slide.status === 'generating' ? 'border-indigo-500/50' : 'border-slate-800'} rounded-xl p-4 flex gap-4 transition-colors ${draggedIndex === index ? 'opacity-50' : 'opacity-100'}`}
                    >
                        <div className="flex flex-col items-center justify-start pt-2 gap-2 text-slate-500 cursor-grab active:cursor-grabbing">
                            <span className="font-bold text-lg">{index + 1}</span>
                            <GripVertical className="w-4 h-4 opacity-50 hover:opacity-100" />
                        </div>
                        
                        <div className="flex-1 space-y-3">
                            <div>
                                <label className="text-xs font-bold text-slate-400 uppercase mb-1 block">Texto na Imagem (Overlay)</label>
                                <input
                                    type="text"
                                    value={slide.overlayText}
                                    onChange={(e) => handleSlideChange(slide.id, 'overlayText', e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
                                    placeholder="Texto curto e chamativo..."
                                />
                            </div>
                            <div>
                                <label className="text-xs font-bold text-slate-400 uppercase mb-1 block">Prompt da Imagem (Fundo)</label>
                                <textarea
                                    value={slide.prompt}
                                    onChange={(e) => handleSlideChange(slide.id, 'prompt', e.target.value)}
                                    className="w-full h-20 bg-slate-900 border border-slate-700 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 resize-none"
                                    placeholder="Descrição visual da cena..."
                                />
                            </div>
                            {slide.error && (
                                <p className="text-xs text-red-400 mt-1">{slide.error}</p>
                            )}
                        </div>

                        <div className="w-32 flex flex-col items-center justify-between border-l border-slate-800 pl-4">
                            {slide.imageUrl ? (
                                <img 
                                    src={slide.imageUrl} 
                                    alt={`Slide ${index + 1}`} 
                                    className="w-full aspect-square object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity"
                                    onClick={() => onImageClick?.({ id: slide.id, imageUrl: slide.imageUrl!, prompt: slide.prompt, timestamp: Date.now(), category: 'social' } as GeneratedImage)}
                                />
                            ) : (
                                <div className="w-full aspect-square bg-slate-900 rounded-lg flex items-center justify-center border border-slate-800">
                                    {slide.status === 'generating' ? (
                                        <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
                                    ) : (
                                        <ImageIcon className="w-6 h-6 text-slate-700" />
                                    )}
                                </div>
                            )}
                            
                            <button
                                onClick={() => handleRemoveSlide(slide.id)}
                                className="text-slate-500 hover:text-red-400 p-1 mt-2 transition-colors"
                                title="Remover Slide"
                            >
                                <Trash2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))
            )}
        </div>
      </div>
    </div>
  );
};

export default CarouselCreator;
