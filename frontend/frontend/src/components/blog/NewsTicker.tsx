import React from 'react';
import Link from 'next/link';

export default function NewsTicker({ posts, domain }: { posts: any[], domain: string }) {
  if (!posts || posts.length === 0) return null;

  return (
    <div className="w-full bg-theme-surface/80 backdrop-blur-md border-b border-theme-border/50 text-theme-text flex items-center overflow-hidden h-11 text-sm shadow-md">
      <div className="bg-theme-accent/20 h-full flex items-center px-6 font-black uppercase tracking-widest text-[10px] whitespace-nowrap z-10 border-r border-theme-accent/30 shadow-[5px_0_15px_rgba(0,0,0,0.5)]">
        <span className="w-2 h-2 rounded-full bg-theme-accent animate-pulse mr-3"></span>
        Flash News
      </div>
      <div className="flex-1 overflow-hidden relative flex items-center">
        <div className="flex whitespace-nowrap animate-[marquee_40s_linear_infinite] hover:[animation-play-state:paused] items-center">
          {posts.concat(posts).map((post, idx) => ( 
            <div key={`${post.id}-${idx}`} className="flex items-center">
              <span className="text-theme-accent/50 mx-6 font-bold">///</span>
              <Link href={`/blog/${post.slug}`} className="hover:text-theme-accent transition-colors font-semibold text-slate-300">
                {post.title}
              </Link>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
