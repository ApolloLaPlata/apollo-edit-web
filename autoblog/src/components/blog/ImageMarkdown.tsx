import React from 'react';
import Image from 'next/image';

/**
 * Interceptor de Imagem
 * Substitui a tag <img> padrão do Markdown pelo componente <Image> ultra otimizado do Next.js
 * Injeta bordas arredondadas e sombras para dar o aspecto visual "premium".
 */
export default function ImageMarkdown({ src, alt }: { src?: string; alt?: string }) {
  if (!src) return null;

  return (
    <span className="block my-10 relative group overflow-hidden rounded-2xl shadow-xl shadow-slate-900/10 dark:shadow-black/50 border border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900">
      <Image
        src={src}
        alt={alt || "Imagem do Artigo"}
        width={800}
        height={450}
        className="w-full h-auto object-cover group-hover:scale-105 transition-transform duration-700 ease-in-out"
        loading="lazy"
        // Placeholder de desfoque simulado
        placeholder="blur"
        blurDataURL="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=" 
      />
      {alt && (
        <span className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
          <span className="text-xs font-medium text-white/90">{alt}</span>
        </span>
      )}
    </span>
  );
}
