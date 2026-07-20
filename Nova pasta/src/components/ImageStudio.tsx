import React, { useState } from 'react';
import { Image as ImageIcon, Loader2, Wand2, Download, RefreshCw } from 'lucide-react';
import { generateAIImage } from '../lib/gemini';

export function ImageStudio() {
  const [prompt, setPrompt] = useState('');
  const [aspectRatio, setAspectRatio] = useState<'16:9' | '1:1' | '9:16'>('16:9');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    setError(null);
    try {
      const base64Image = await generateAIImage(prompt, aspectRatio);
      setGeneratedImage(base64Image);
    } catch (err: any) {
      console.error('Error generating image:', err);
      setError('Falha ao gerar a imagem. Tente novamente com um prompt diferente.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!generatedImage) return;
    const a = document.createElement('a');
    a.href = generatedImage;
    a.download = `thumbnail-${Date.now()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-sm border border-zinc-200 p-6">
        <h2 className="text-2xl font-bold text-zinc-900 mb-2 flex items-center gap-2">
          <ImageIcon className="text-indigo-600" size={28} />
          Estúdio de Capas
        </h2>
        <p className="text-zinc-600 mb-6">
          Crie thumbnails e imagens exclusivas para os seus vídeos usando Inteligência Artificial.
        </p>
        
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="block text-sm font-medium text-zinc-700">
                Descreva a imagem que você quer gerar:
              </label>
              {prompt.trim() && (
                <button 
                  onClick={() => setPrompt('')}
                  className="text-xs text-zinc-500 hover:text-red-500 transition-colors"
                >
                  Limpar
                </button>
              )}
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ex: Bolsonaro e Lula debatendo em um estúdio escuro, iluminação dramática, estilo capa de vídeo do YouTube, alta qualidade"
              className="w-full rounded-md bg-white border border-zinc-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 min-h-[100px] p-3"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="flex gap-2">
              {(['16:9', '1:1', '9:16'] as const).map((ratio) => (
                <button
                  key={ratio}
                  onClick={() => setAspectRatio(ratio)}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors border ${
                    aspectRatio === ratio
                      ? 'bg-indigo-50 border-indigo-200 text-indigo-700'
                      : 'bg-white border-zinc-200 text-zinc-600 hover:bg-zinc-50'
                  }`}
                >
                  {ratio === '16:9' ? 'Thumbnail (16:9)' : ratio === '1:1' ? 'Quadrado (1:1)' : 'Shorts (9:16)'}
                </button>
              ))}
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !prompt.trim()}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-md font-medium transition-colors flex items-center gap-2 disabled:opacity-50 w-full sm:w-auto justify-center"
            >
              {isGenerating ? <Loader2 size={20} className="animate-spin" /> : <Wand2 size={20} />}
              Gerar Imagem
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-100">
          {error}
        </div>
      )}

      {isGenerating && (
        <div className="bg-white rounded-xl border border-zinc-200 p-12 flex flex-col items-center justify-center text-zinc-500">
          <Loader2 size={48} className="animate-spin mb-4 text-indigo-600" />
          <p className="text-lg font-medium">Criando sua imagem...</p>
          <p className="text-sm mt-2">Isso pode levar alguns segundos.</p>
        </div>
      )}

      {generatedImage && !isGenerating && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-lg text-zinc-900">Resultado</h3>
            <div className="flex gap-2">
              <button
                onClick={handleGenerate}
                className="p-2 text-zinc-600 hover:bg-zinc-100 rounded-md transition-colors"
                title="Gerar novamente"
              >
                <RefreshCw size={20} />
              </button>
              <button
                onClick={handleDownload}
                className="flex items-center gap-2 px-4 py-2 bg-zinc-900 hover:bg-zinc-800 text-white rounded-md font-medium transition-colors"
              >
                <Download size={16} />
                Baixar
              </button>
            </div>
          </div>
          
          <div className={`bg-zinc-100 rounded-lg overflow-hidden flex items-center justify-center ${
            aspectRatio === '16:9' ? 'aspect-video' : aspectRatio === '1:1' ? 'aspect-square max-w-2xl mx-auto' : 'aspect-[9/16] max-w-md mx-auto'
          }`}>
            <img 
              src={generatedImage} 
              alt="Imagem gerada" 
              className="w-full h-full object-contain"
            />
          </div>
        </div>
      )}
    </div>
  );
}
