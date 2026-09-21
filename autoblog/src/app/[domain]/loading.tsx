'use client';
import React from 'react';

export default function Loading() {
  return (
    <div className="min-h-screen bg-theme-bg text-theme-text pt-24 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Header Skeleton */}
      <div className="flex flex-col items-center justify-center mb-16 animate-pulse">
        <div className="w-48 h-8 bg-theme-surface rounded-md mb-4 border border-theme-border"></div>
        <div className="w-96 h-4 bg-theme-surface rounded-md mb-2 opacity-50"></div>
        <div className="w-64 h-4 bg-theme-surface rounded-md opacity-50"></div>
      </div>

      {/* Grid Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="glass-card flex flex-col h-full animate-pulse border border-theme-border">
            {/* Image Placeholder */}
            <div className="w-full h-48 bg-theme-surface/50 border-b border-theme-border"></div>
            
            {/* Content Placeholder */}
            <div className="p-6 flex-1 flex flex-col">
              <div className="w-20 h-4 bg-theme-accent/20 rounded-full mb-4"></div>
              <div className="w-full h-6 bg-theme-surface rounded-md mb-3"></div>
              <div className="w-3/4 h-6 bg-theme-surface rounded-md mb-6"></div>
              
              <div className="mt-auto flex items-center justify-between">
                <div className="w-24 h-4 bg-theme-surface rounded-md"></div>
                <div className="w-8 h-8 bg-theme-surface rounded-full"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
