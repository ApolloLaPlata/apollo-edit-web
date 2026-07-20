import React, { useEffect } from 'react';
import { X, ChevronLeft, ChevronRight, Download, ExternalLink, RefreshCw, Loader2 } from 'lucide-react';
import { GeneratedImage } from '../types';

interface LightboxProps {
  isOpen: boolean;
  onClose: () => void;
  image: GeneratedImage | null;
  onNext?: () => void;
  onPrev?: () => void;
  hasNext?: boolean;
  hasPrev?: boolean;
  onRegenerate?: (image: GeneratedImage) => void;
  isRegenerating?: boolean;
}

const Lightbox: React.FC<LightboxProps> = ({
  isOpen,
  onClose,
  image,
  onNext,
  onPrev,
  hasNext,
  hasPrev,
  onRegenerate,
  isRegenerating,
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowRight' && onNext && hasNext) onNext();
      if (e.key === 'ArrowLeft' && onPrev && hasPrev) onPrev();
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose, onNext, onPrev, hasNext, hasPrev]);

  if (!isOpen || !image) return null;

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    const link = document.createElement('a');
    if (image.videoUrl) {
      link.href = image.videoUrl;
      link.download = `video_${image.id.slice(0, 8)}.mp4`;
    } else {
      link.href = image.imageUrl;
      link.download = `image_${image.id.slice(0, 8)}.png`;
    }
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div 
      className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center backdrop-blur-sm"
      onClick={onClose}
    >
      {/* Close Button */}
      <button 
        onClick={onClose}
        className="absolute top-4 right-4 text-slate-400 hover:text-white p-2 rounded-full hover:bg-white/10 transition-colors z-50"
      >
        <X className="w-8 h-8" />
      </button>

      {/* Navigation - Left */}
      {hasPrev && (
        <button
          onClick={(e) => { e.stopPropagation(); onPrev?.(); }}
          className="absolute left-4 top-1/2 -translate-y-1/2 text-white/50 hover:text-white p-4 rounded-full hover:bg-white/10 transition-colors z-50"
        >
          <ChevronLeft className="w-10 h-10" />
        </button>
      )}

      {/* Navigation - Right */}
      {hasNext && (
        <button
          onClick={(e) => { e.stopPropagation(); onNext?.(); }}
          className="absolute right-4 top-1/2 -translate-y-1/2 text-white/50 hover:text-white p-4 rounded-full hover:bg-white/10 transition-colors z-50"
        >
          <ChevronRight className="w-10 h-10" />
        </button>
      )}

      {/* Main Content */}
      <div 
        className="relative max-w-[90vw] max-h-[90vh] flex flex-col items-center gap-4"
        onClick={(e) => e.stopPropagation()}
      >
        {image.videoUrl ? (
          <video 
            src={image.videoUrl} 
            autoPlay 
            loop 
            controls
            className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
          />
        ) : (
          <img 
            src={image.imageUrl} 
            alt={image.prompt} 
            className="max-w-full max-h-[80vh] object-contain rounded-lg shadow-2xl"
          />
        )}
        
        <div className="w-full bg-black/50 backdrop-blur-md p-4 rounded-xl border border-white/10 flex flex-col gap-2">
          <p className="text-white text-sm font-medium line-clamp-2 text-center">
            {image.prompt}
          </p>
          
          <div className="flex items-center justify-center gap-4 mt-2">
            <button 
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 bg-white text-black rounded-full font-bold text-sm hover:bg-slate-200 transition-colors"
            >
              <Download className="w-4 h-4" /> Baixar Original
            </button>
            
            {onRegenerate && (
              <button 
                onClick={(e) => { e.stopPropagation(); onRegenerate(image); }}
                disabled={isRegenerating}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-full font-bold text-sm hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isRegenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                {isRegenerating ? 'Regenerando...' : 'Regenerar'}
              </button>
            )}
            
            {image.videoPrompt && (
              <div className="flex items-center gap-2 px-3 py-1 bg-purple-900/40 border border-purple-500/30 rounded-full text-xs text-purple-200">
                <ExternalLink className="w-3 h-3" /> Prompt de Vídeo Disponível
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Lightbox;
