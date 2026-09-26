'use client';
import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import ImageWithBlur from '@/components/ui/ImageWithBlur';
import type { PostData } from './templates/LayoutRouter';
import ScrollReveal from './ScrollReveal';

function cleanExcerpt(markdown: string, maxLen = 180): string {
  return markdown
    .replace(/[#*`_\[\]>!]/g, '')
    .replace(/={3,}/g, '')
    .replace(/-/g, '')
    .replace(/Este é um artigo gerado automaticamente.*?\./gi, '')
    .replace(/Não posso atender a esta solicitação.*?\./gi, '')
    .replace(/\s+/g, ' ')
    .trim()
    .substring(0, maxLen);
}

function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch {
    return iso;
  }
}

interface InfiniteScrollProps {
  blogId: string;
  initialOffset: number;
  lang: string;
  domain: string;
  primaryColor?: string;
}

export default function InfiniteScrollLoader({ blogId, initialOffset, lang, domain, primaryColor = '#7c3aed' }: InfiniteScrollProps) {
  const [posts, setPosts] = useState<PostData[]>([]);
  const [offset, setOffset] = useState(initialOffset);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef<HTMLDivElement>(null);

  const fetchPosts = async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/posts?blogId=${blogId}&lang=${lang}&offset=${offset}&limit=6`);
      if (!res.ok) throw new Error('Falha ao carregar posts');
      const data = await res.json();
      
      if (data.posts && data.posts.length > 0) {
        setPosts(prev => [...prev, ...data.posts]);
        setOffset(prev => prev + data.posts.length);
      } else {
        setHasMore(false);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          fetchPosts();
        }
      },
      { rootMargin: '400px' } // Começa a carregar 400px antes de chegar no fim
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => observer.disconnect();
  }, [hasMore, loading, offset, blogId, lang]); // Dependências completas para re-trigger

  return (
    <>
      {posts.map((post, idx) => (
        <ScrollReveal key={`${post.id}-${idx}`} delay={(idx % 6) * 0.1}>
          <article className="glass-card group flex flex-col justify-between h-full animate-toast-slide-up" style={{ animationDuration: '0.4s' }}>
            <div className="flex flex-col h-full">
              <Link href={`/blog/${post.slug}`} className="block relative h-48 w-full overflow-hidden">
                {post.coverImage ? (
                  <ImageWithBlur
                    src={post.coverImage}
                    alt={post.title}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700 ease-out"
                    containerClassName="w-full h-full"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center" style={{ background: `linear-gradient(135deg, #1e293b, ${primaryColor}30)` }}>
                    <span className="text-3xl opacity-30">📄</span>
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-60 group-hover:opacity-40 transition-opacity" />
                
                {post.category && (
                  <span className="absolute top-3 left-3 px-2.5 py-1 rounded-lg text-[9px] font-black uppercase tracking-wider bg-black/70 text-white backdrop-blur-md border border-white/10">
                    {post.category}
                  </span>
                )}
              </Link>

              <div className="p-5 space-y-2.5">
                <div className="flex items-center justify-between text-[10px] text-theme-muted font-mono font-bold">
                  <span>📅 {fmtDate(post.createdAt)}</span>
                  <span>⏱️ ~{Math.max(1, Math.ceil(post.contentMd.length / 800))} min</span>
                </div>

                <Link href={`/blog/${post.slug}`}>
                  <h3 className="font-extrabold text-base text-theme-text leading-snug line-clamp-2 group-hover:text-theme-accent transition-colors">
                    {post.title}
                  </h3>
                </Link>

                <p className="text-xs text-theme-muted line-clamp-2 leading-relaxed font-normal">
                  {cleanExcerpt(post.contentMd, 120)}...
                </p>
              </div>
            </div>

            <div className="px-5 py-3.5 bg-theme-bg/50 border-t border-theme-border/60 flex items-center justify-between text-[11px] font-extrabold">
              <span className="text-theme-muted truncate max-w-[140px]">✍️ {post.author}</span>
              <Link href={`/blog/${post.slug}`} className="text-theme-accent group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                <span>Ler</span>
                <span>→</span>
              </Link>
            </div>
          </article>
        </ScrollReveal>
      ))}
      
      {hasMore && (
        <div ref={observerRef} className="col-span-1 sm:col-span-2 xl:col-span-3 py-12 flex justify-center items-center">
          {loading ? (
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 border-4 border-theme-accent border-t-transparent rounded-full animate-spin"></div>
              <span className="text-[10px] font-bold text-theme-muted uppercase tracking-[0.2em]">Carregando Acervo...</span>
            </div>
          ) : (
            <div className="h-8"></div>
          )}
        </div>
      )}
    </>
  );
}
