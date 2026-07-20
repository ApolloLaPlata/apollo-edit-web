import React, { useState, useEffect } from 'react';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  message: string;
  type: ToastType;
}

export function ToastContainer() {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  useEffect(() => {
    const handleAddToast = (e: CustomEvent<ToastMessage>) => {
      setToasts(prev => [...prev, e.detail]);
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== e.detail.id));
      }, 3000);
    };

    window.addEventListener('add-toast' as any, handleAddToast);
    return () => window.removeEventListener('add-toast' as any, handleAddToast);
  }, []);

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map(toast => (
        <div key={toast.id} className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg border ${
          toast.type === 'success' ? 'bg-emerald-900/30 border-emerald-200 text-emerald-800' :
          toast.type === 'error' ? 'bg-red-900/30 border-red-200 text-red-800' :
          'bg-blue-50 border-blue-200 text-blue-800'
        } transition-all duration-300`}>
          {toast.type === 'success' && <CheckCircle2 size={20} className="text-emerald-600 shrink-0" />}
          {toast.type === 'error' && <AlertCircle size={20} className="text-red-600 shrink-0" />}
          {toast.type === 'info' && <Info size={20} className="text-blue-600 shrink-0" />}
          <p className="font-medium text-sm">{toast.message}</p>
          <button onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))} className="ml-2 opacity-50 hover:opacity-100 shrink-0">
            <X size={16} />
          </button>
        </div>
      ))}
    </div>
  );
}

export const toast = {
  success: (message: string) => {
    window.dispatchEvent(new CustomEvent('add-toast', { detail: { id: Math.random().toString(36).substring(2, 9), message, type: 'success' } }));
  },
  error: (message: string) => {
    window.dispatchEvent(new CustomEvent('add-toast', { detail: { id: Math.random().toString(36).substring(2, 9), message, type: 'error' } }));
  },
  info: (message: string) => {
    window.dispatchEvent(new CustomEvent('add-toast', { detail: { id: Math.random().toString(36).substring(2, 9), message, type: 'info' } }));
  }
};
