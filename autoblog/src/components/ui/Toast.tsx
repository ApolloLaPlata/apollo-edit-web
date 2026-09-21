'use client';
import React, { useEffect, useState } from 'react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastItem {
  id: string;
  message: string;
  type: ToastType;
}

type Listener = (toast: ToastItem) => void;
let listeners: Listener[] = [];

export const toast = {
  success: (message: string) => dispatchToast(message, 'success'),
  error: (message: string) => dispatchToast(message, 'error'),
  info: (message: string) => dispatchToast(message, 'info'),
};

const ICONS: Record<string, React.ReactNode> = {
  success: (
    <svg className="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  error: (
    <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  info: (
    <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  )
};

export default function Toast({ message, type, onClose }: { message: string, type: ToastType, onClose: () => void }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed bottom-24 md:bottom-6 right-0 md:right-6 z-[9999] p-4 pointer-events-none w-full md:w-auto items-end flex flex-col gap-3">
      <div className="animate-toast-slide-up flex items-center gap-3 py-3 px-4 min-w-[280px] max-w-sm pointer-events-auto bg-theme-surface/90 backdrop-blur-xl border border-theme-border/50 shadow-2xl rounded-2xl relative overflow-hidden group">
        <div className={`absolute left-0 top-0 bottom-0 w-1 ${type === 'success' ? 'bg-emerald-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}></div>
        <div className="shrink-0 pl-2">
          {ICONS[type] || ICONS['info']}
        </div>
        <div className="text-sm font-semibold text-theme-text flex-1">
          {message}
        </div>
        <button onClick={onClose} className="text-theme-muted hover:text-theme-text transition-colors shrink-0">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
    </div>
  );
}

function dispatchToast(message: string, type: ToastType) {
  const id = Math.random().toString(36).substring(2, 9);
  listeners.forEach(l => l({ id, message, type }));
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    const listener = (t: ToastItem) => {
      setToasts(prev => [...prev, t]);
      // Remove automatically after 4 seconds
      setTimeout(() => {
        setToasts(prev => prev.filter(x => x.id !== t.id));
      }, 4000);
    };

    listeners.push(listener);
    return () => {
      listeners = listeners.filter(l => l !== listener);
    };
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-24 md:bottom-6 right-0 md:right-6 z-[9999] flex flex-col gap-3 p-4 pointer-events-none w-full md:w-auto items-end">
      {toasts.map(t => (
        <div 
          key={t.id} 
          className="animate-toast-slide-up flex items-center gap-3 py-3 px-4 min-w-[280px] max-w-sm pointer-events-auto bg-theme-surface/90 backdrop-blur-xl border border-theme-border/50 shadow-2xl rounded-2xl relative overflow-hidden group"
        >
          {/* Indicador de cor à esquerda */}
          <div className={`absolute left-0 top-0 bottom-0 w-1 ${t.type === 'success' ? 'bg-emerald-500' : t.type === 'error' ? 'bg-red-500' : 'bg-blue-500'}`}></div>
          
          <div className="shrink-0 pl-2">
            {ICONS[t.type]}
          </div>
          
          <div className="text-sm font-semibold text-theme-text flex-1">
            {t.message}
          </div>
          
          <button 
            onClick={() => setToasts(prev => prev.filter(x => x.id !== t.id))}
            className="text-theme-muted hover:text-theme-text transition-colors shrink-0"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
      ))}
    </div>
  );
}
