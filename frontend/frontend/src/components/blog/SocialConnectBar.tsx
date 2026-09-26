"use client";

import React, { useState } from 'react';
import Link from 'next/link';

interface SocialLinksMap {
  youtube?: string;
  facebook?: string;
  instagram?: string;
  twitter?: string;
  tiktok?: string;
  kwai?: string;
  dailymotion?: string;
  newsletter?: string;
  [key: string]: string | undefined;
}

interface SocialConnectBarProps {
  socialLinksRaw?: string;
  primaryColor?: string;
  siteName?: string;
  layout?: 'bar' | 'grid' | 'compact';
}

export default function SocialConnectBar({
  socialLinksRaw,
  primaryColor = '#3b82f6',
  siteName = 'Portal',
  layout = 'bar'
}: SocialConnectBarProps) {
  const [showNewsletterForm, setShowNewsletterForm] = useState(false);
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);

  let links: SocialLinksMap = {};
  try {
    if (socialLinksRaw) {
      links = JSON.parse(socialLinksRaw);
    } else {
      // Fallback padrão se não houver links cadastrados
      links = {
        youtube: 'https://youtube.com',
        facebook: 'https://facebook.com',
        instagram: 'https://instagram.com',
        twitter: 'https://x.com',
        tiktok: 'https://tiktok.com',
        kwai: 'https://kwai.com',
        dailymotion: 'https://dailymotion.com',
        newsletter: '#subscribe'
      };
    }
  } catch {
    links = {};
  }

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !email.includes('@')) return;
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSubscribed(true);
      setEmail('');
    }, 800);
  };

  const platforms = [
    {
      id: 'youtube',
      name: 'YouTube',
      label: 'Vídeos & Shorts',
      url: links.youtube,
      color: '#FF0000',
      bgHover: 'hover:bg-[#FF0000]/15 hover:border-[#FF0000]/40 hover:text-[#FF0000]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
      )
    },
    {
      id: 'facebook',
      name: 'Facebook',
      label: 'Comunidade & Página',
      url: links.facebook,
      color: '#1877F2',
      bgHover: 'hover:bg-[#1877F2]/15 hover:border-[#1877F2]/40 hover:text-[#1877F2]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      )
    },
    {
      id: 'instagram',
      name: 'Instagram',
      label: 'Feed, Reels & Stories',
      url: links.instagram,
      color: '#E1306C',
      bgHover: 'hover:bg-[#E1306C]/15 hover:border-[#E1306C]/40 hover:text-[#E1306C]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
      )
    },
    {
      id: 'twitter',
      name: 'X / Twitter',
      label: 'Notícias & Threads',
      url: links.twitter,
      color: '#ffffff',
      bgHover: 'hover:bg-white/15 hover:border-white/40 hover:text-white',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
        </svg>
      )
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      label: 'Vídeos Curtos Virais',
      url: links.tiktok,
      color: '#00f2fe',
      bgHover: 'hover:bg-[#00f2fe]/15 hover:border-[#00f2fe]/40 hover:text-[#00f2fe]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/>
        </svg>
      )
    },
    {
      id: 'kwai',
      name: 'Kwai',
      label: 'Vídeos & Engajamento',
      url: links.kwai,
      color: '#FF8000',
      bgHover: 'hover:bg-[#FF8000]/15 hover:border-[#FF8000]/40 hover:text-[#FF8000]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M15.01 2H8.99C4.1 2 2 4.1 2 8.99v6.02C2 19.9 4.1 22 8.99 22h6.02c4.89 0 6.99-2.1 6.99-6.99V8.99C22 4.1 19.9 2 15.01 2zM17.43 16.5c-.32.41-.78.63-1.28.63-.35 0-.69-.11-.98-.32l-2.93-2.16-1.57 1.57c-.29.29-.68.45-1.09.45-.41 0-.8-.16-1.09-.45-.6-.6-.6-1.58 0-2.18l2.3-2.3-2.3-2.3c-.6-.6-.6-1.58 0-2.18.6-.6 1.58-.6 2.18 0l1.57 1.57 2.93-2.16c.59-.44 1.4-.41 1.95.09.58.53.64 1.42.15 2.03L15.35 12l1.93 2.47c.49.61.43 1.5-.15 2.03z"/>
        </svg>
      )
    },
    {
      id: 'dailymotion',
      name: 'Dailymotion',
      label: 'Canal de Vídeos HD',
      url: links.dailymotion,
      color: '#0066DC',
      bgHover: 'hover:bg-[#0066DC]/15 hover:border-[#0066DC]/40 hover:text-[#0066DC]',
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M12.01 2.02c-5.52 0-9.99 4.47-9.99 9.99s4.47 9.99 9.99 9.99c2.25 0 4.33-.74 5.99-1.99v1.27h3.98V8.69h-3.98v1.28c-1.66-1.25-3.74-1.99-5.99-1.99zm0 15.98c-3.31 0-5.99-2.68-5.99-5.99s2.68-5.99 5.99-5.99 5.99 2.68 5.99 5.99-2.68 5.99-5.99 5.99z"/>
        </svg>
      )
    },
    {
      id: 'newsletter',
      name: 'Newsletter',
      label: 'Daily Drop no E-mail',
      url: links.newsletter || '#subscribe',
      color: '#10B981',
      bgHover: 'hover:bg-[#10B981]/15 hover:border-[#10B981]/40 hover:text-[#10B981]',
      isNewsletter: true,
      icon: (
        <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
          <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
        </svg>
      )
    }
  ];

  // Filtra apenas as plataformas que possuem URL cadastrada ou que são newsletter
  const activePlatforms = platforms.filter(p => p.url && p.url.trim() !== '' && p.url !== '#');

  if (activePlatforms.length === 0) return null;

  return (
    <div className="w-full bg-slate-950/90 border-y border-slate-800/80 py-8 my-8 text-slate-200 relative overflow-hidden shadow-2xl">
      {/* Brilho de fundo sutil */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-32 blur-3xl opacity-10 pointer-events-none rounded-full"
        style={{ backgroundColor: primaryColor }}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-6 pb-6 border-b border-slate-800/80">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-2" style={{ backgroundColor: `${primaryColor}20`, color: primaryColor, border: `1px solid ${primaryColor}40` }}>
              <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: primaryColor }} />
              <span>Conecte-se com {siteName}</span>
            </div>
            <h3 className="text-xl md:text-2xl font-black text-white tracking-tight">
              Acompanhe nosso conteúdo em todas as redes
            </h3>
            <p className="text-slate-400 text-xs md:text-sm mt-1 max-w-xl">
              Vídeos longos, shorts virais, comunidade ativa e alertas de notícias diretos. Escolha seu canal preferido:
            </p>
          </div>

          {!showNewsletterForm && (
            <button
              onClick={() => setShowNewsletterForm(true)}
              className="px-5 py-2.5 rounded-xl font-bold text-xs uppercase tracking-wider text-white shadow-lg transition-all hover:scale-105 flex items-center gap-2 shrink-0 border border-white/20"
              style={{ backgroundColor: primaryColor }}
            >
              <span>✉️</span>
              <span>Assinar Newsletter VIP</span>
            </button>
          )}
        </div>

        {/* Grid dos Canais Sociais */}
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
          {activePlatforms.map((p) => {
            if (p.isNewsletter) {
              return (
                <button
                  key={p.id}
                  onClick={() => setShowNewsletterForm(!showNewsletterForm)}
                  className={`p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col items-center justify-center text-center transition-all duration-300 group ${p.bgHover} shadow-sm`}
                >
                  <div className="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform text-slate-300 group-hover:text-current">
                    {p.icon}
                  </div>
                  <span className="text-xs font-bold text-white group-hover:text-current transition-colors">
                    {p.name}
                  </span>
                  <span className="text-[10px] text-slate-400 font-medium line-clamp-1 mt-0.5">
                    {p.label}
                  </span>
                </button>
              );
            }

            return (
              <a
                key={p.id}
                href={p.url}
                target="_blank"
                rel="noopener noreferrer"
                className={`p-3 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col items-center justify-center text-center transition-all duration-300 group ${p.bgHover} shadow-sm`}
              >
                <div className="w-10 h-10 rounded-xl bg-slate-800/80 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform text-slate-300 group-hover:text-current">
                  {p.icon}
                </div>
                <span className="text-xs font-bold text-white group-hover:text-current transition-colors">
                  {p.name}
                </span>
                <span className="text-[10px] text-slate-400 font-medium line-clamp-1 mt-0.5">
                  {p.label}
                </span>
              </a>
            );
          })}
        </div>

        {/* Formulário de Newsletter Expansível (Zero Native Dialogs) */}
        {showNewsletterForm && (
          <div className="mt-6 pt-6 border-t border-slate-800/80 animate-fadeIn">
            <div className="bg-slate-900/90 rounded-2xl p-6 border border-slate-800 relative max-w-2xl mx-auto shadow-xl">
              <button
                onClick={() => setShowNewsletterForm(false)}
                className="absolute top-4 right-4 text-slate-400 hover:text-white text-sm font-bold w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center"
                title="Fechar"
              >
                ✕
              </button>

              <div className="text-center mb-4">
                <span className="text-2xl mb-1 block">✉️</span>
                <h4 className="text-lg font-black text-white">
                  Inscreva-se na Newsletter de {siteName}
                </h4>
                <p className="text-xs text-slate-400 mt-1">
                  Receba nossa pílula diária de notícias (Daily Drop), análises aprofundadas e alertas de novas séries direto na sua caixa de entrada. Sem spam.
                </p>
              </div>

              {subscribed ? (
                <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-center font-bold text-sm flex items-center justify-center gap-2 animate-bounce">
                  <span>🎉</span>
                  <span>Inscrito com sucesso! Verifique sua caixa de entrada em breve.</span>
                </div>
              ) : (
                <form onSubmit={handleSubscribe} className="flex flex-col sm:flex-row gap-3 mt-4">
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Digite seu melhor e-mail corporativo ou pessoal..."
                    required
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors font-medium shadow-inner"
                  />
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider text-white shadow-lg transition-all hover:opacity-90 disabled:opacity-50 shrink-0 flex items-center justify-center gap-2"
                    style={{ backgroundColor: primaryColor }}
                  >
                    {loading ? (
                      <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <span>Assinar Daily Drop</span>
                        <span>🚀</span>
                      </>
                    )}
                  </button>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
