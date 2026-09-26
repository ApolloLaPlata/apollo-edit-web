'use client';
import React from 'react';

export default function AdminLoading() {
  return (
    <div className="flex flex-col items-center justify-center h-full bg-slate-900 text-slate-300 min-h-[50vh]">
      <div className="relative w-24 h-24 mb-6">
        <div className="absolute inset-0 border-4 border-slate-800 rounded-xl"></div>
        <div className="absolute inset-0 border-4 border-blue-500 rounded-xl border-t-transparent animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center text-blue-500">
          <svg className="w-8 h-8 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
        </div>
      </div>
      <h2 className="text-xl font-bold uppercase tracking-widest text-white mb-2">Iniciando Módulos</h2>
      <p className="text-slate-500 font-medium text-xs uppercase tracking-widest animate-pulse">Aguarde, extraindo dados seguros...</p>
    </div>
  );
}
