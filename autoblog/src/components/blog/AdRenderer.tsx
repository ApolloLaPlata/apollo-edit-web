'use client';
import React, { useEffect, useRef } from 'react';

export default function AdRenderer({ html, className }: { html: string, className?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // React's dangerouslySetInnerHTML doesn't execute <script> tags.
    // We need to manually extract and run them for Affiliate tracking scripts and AdSense.
    const scripts = containerRef.current.querySelectorAll('script');
    
    scripts.forEach(oldScript => {
      // Don't re-run scripts if they already executed (basic check)
      if (oldScript.getAttribute('data-executed')) return;
      
      const newScript = document.createElement('script');
      
      Array.from(oldScript.attributes).forEach(attr => {
        newScript.setAttribute(attr.name, attr.value);
      });
      
      newScript.appendChild(document.createTextNode(oldScript.innerHTML));
      newScript.setAttribute('data-executed', 'true');
      
      if (oldScript.parentNode) {
        oldScript.parentNode.replaceChild(newScript, oldScript);
      }
    });

    // Special trigger for Google AdSense <ins> blocks
    if (html.includes('adsbygoogle')) {
      try {
        (window as any).adsbygoogle = (window as any).adsbygoogle || [];
        (window as any).adsbygoogle.push({});
      } catch (e) {
        console.error("[AdSense] Falha ao injetar bloco:", e);
      }
    }
  }, [html]);

  return (
    <div ref={containerRef} className={className} dangerouslySetInnerHTML={{ __html: html }} />
  );
}
