'use client';
import React, { useState } from 'react';

interface ImageWithBlurProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  containerClassName?: string;
  fallbackColor?: string; // Cor sólida de fundo enquanto carrega
}

export default function ImageWithBlur({ 
  src, 
  alt, 
  className = '', 
  containerClassName = '',
  fallbackColor = 'var(--color-theme-surface)',
  ...props 
}: ImageWithBlurProps) {
  const [isLoaded, setIsLoaded] = useState(false);

  return (
    <div 
      className={`relative overflow-hidden ${containerClassName}`}
      style={{ backgroundColor: isLoaded ? 'transparent' : fallbackColor }}
    >
      {/* Esqueleto animado de fundo se a imagem demorar muito */}
      {!isLoaded && (
        <div className="absolute inset-0 animate-pulse bg-white/5 pointer-events-none"></div>
      )}
      
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={src}
        alt={alt}
        className={`${className} transition-opacity duration-700 ease-in-out ${isLoaded ? 'opacity-100' : 'opacity-0'}`}
        onLoad={() => setIsLoaded(true)}
        {...props}
      />
    </div>
  );
}
