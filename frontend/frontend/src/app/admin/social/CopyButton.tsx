'use client';

import React, { useState } from 'react';

export default function CopyButton({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      className={`flex-1 px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-sm active:scale-95 ${
        copied
          ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-500/20'
          : 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20'
      }`}
    >
      {copied ? (
        <>
          <span>✓</span>
          <span>Copiado!</span>
        </>
      ) : (
        <>
          <span>📋</span>
          <span>Copiar Isca</span>
        </>
      )}
    </button>
  );
}
