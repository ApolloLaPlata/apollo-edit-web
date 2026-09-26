'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Evitar hidration mismatch
  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="w-9 h-9 rounded-full bg-white/5 animate-pulse" />;
  }

  const isDark = theme === 'dark';

  return (
    <button
      onClick={() => setTheme(isDark ? 'light' : 'dark')}
      className="relative w-14 h-7 rounded-full bg-black/40 border border-white/10 shadow-inner flex items-center p-1 transition-colors duration-500 overflow-hidden"
      title={isDark ? "Mudar para Modo Claro" : "Mudar para Modo Escuro"}
    >
      {/* Background estrelado (escuro) */}
      <div 
        className={`absolute inset-0 transition-opacity duration-500 ${isDark ? 'opacity-100' : 'opacity-0'}`} 
      >
        <span className="absolute top-[3px] left-[6px] w-[2px] h-[2px] bg-white rounded-full"></span>
        <span className="absolute top-[8px] left-[14px] w-[1px] h-[1px] bg-white rounded-full opacity-70"></span>
        <span className="absolute bottom-[5px] left-[10px] w-[2px] h-[2px] bg-white rounded-full opacity-50"></span>
      </div>

      {/* Background céu (claro) */}
      <div 
        className={`absolute inset-0 bg-sky-200 transition-opacity duration-500 ${isDark ? 'opacity-0' : 'opacity-100'}`} 
      >
        <span className="absolute top-[4px] right-[8px] w-[8px] h-[4px] bg-white rounded-full opacity-80"></span>
        <span className="absolute bottom-[6px] right-[14px] w-[10px] h-[3px] bg-white rounded-full opacity-60"></span>
      </div>

      {/* A "Moeda" que desliza */}
      <div 
        className={`w-6 h-6 rounded-full shadow-md z-10 flex items-center justify-center transition-transform duration-500 cubic-bezier(0.68, -0.55, 0.265, 1.55) ${isDark ? 'translate-x-7 bg-slate-800' : 'translate-x-0 bg-yellow-400'}`}
      >
        {isDark ? (
          // Lua
          <svg className="w-3.5 h-3.5 text-yellow-100" fill="currentColor" viewBox="0 0 24 24">
             <path d="M21.752 15.002A9.718 9.718 0 0118 15c-5.523 0-10-4.477-10-10 0-1.293.245-2.527.688-3.664a9.752 9.752 0 1013.064 13.666z" />
          </svg>
        ) : (
          // Sol
          <svg className="w-3.5 h-3.5 text-orange-600" fill="currentColor" viewBox="0 0 24 24">
             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" stroke="currentColor" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        )}
      </div>
    </button>
  );
}
