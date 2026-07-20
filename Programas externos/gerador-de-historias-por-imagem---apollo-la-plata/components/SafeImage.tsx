import React, { useState, useEffect } from 'react';
import { ImageOff } from 'lucide-react';

interface SafeImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
}

const SafeImage: React.FC<SafeImageProps> = ({ src, alt, className, ...props }) => {
  const [currentSrc, setCurrentSrc] = useState(src);
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setCurrentSrc(src);
    setHasError(false);
    setIsLoading(true);
  }, [src]);

  const handleError = () => {
    if (!hasError) {
        // First attempt: Try proxying through wsrv.nl to bypass CORS/Referrer
        if (!currentSrc.includes('wsrv.nl') && !currentSrc.startsWith('data:')) {
            console.log("Image failed to load, trying proxy...", src);
            setHasError(true); // Mark as having errored once to prevent loops
            setCurrentSrc(`https://wsrv.nl/?url=${encodeURIComponent(src)}`);
        } else {
            // If proxy fails or it was already a data URL, give up
            setIsLoading(false);
        }
    } else {
        setIsLoading(false);
    }
  };

  const handleLoad = () => {
      setIsLoading(false);
  };

  if (hasError && !isLoading && currentSrc.includes('wsrv.nl')) {
      // If proxy also failed (onError called again)
      return (
          <div className={`bg-slate-800 flex flex-col items-center justify-center text-slate-500 p-4 ${className}`} style={{ minHeight: '150px' }}>
              <ImageOff className="w-8 h-8 mb-2 opacity-50" />
              <span className="text-xs text-center">Falha ao carregar imagem</span>
          </div>
      );
  }

  return (
    <img 
      src={currentSrc} 
      alt={alt} 
      className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
      onError={handleError}
      onLoad={handleLoad}
      referrerPolicy="no-referrer"
      {...props} 
    />
  );
};

export default SafeImage;
