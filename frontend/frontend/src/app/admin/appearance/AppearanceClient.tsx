'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { saveAppearance } from './actions';

interface Blog {
  id: string;
  name: string;
  domain: string;
  niche: string;
  description: string;
  theme: string;
  primaryColor?: string;
  secondaryColor?: string;
  layoutStyle?: string;
  bgPrimary?: string;
  bgSurface?: string;
  fontHeading?: string;
  fontBody?: string;
  bannerUrl?: string;
  fontFamily?: string;
  logoUrl?: string;
  accentStyle?: string;
  activeFeatures?: string;
  socialLinks?: string;
}

// ───────────────────────────────────────────────
// BIBLIOTECA DE TEMAS (20 variantes únicas)
// ───────────────────────────────────────────────
const THEME_PRESETS = [
  // ── DARK FAMILY ──────────────────────────────
  {
    id: 'obsidian_noir',
    label: 'Obsidian Noir',
    emoji: '🖤',
    category: 'Dark Premium',
    desc: 'Preto profundo com acentos prata. Elegância absoluta.',
    primary: '#e2e8f0',
    secondary: '#94a3b8',
    bg: 'bg-black',
    border: 'border-neutral-900',
    text: 'text-white',
    accent: '#e2e8f0',
    preview: { bg: '#000000', card: '#111111', border: '#222222', pill: '#e2e8f0' },
  },
  {
    id: 'midnight_purple',
    label: 'Midnight Purple',
    emoji: '🔮',
    category: 'Dark Premium',
    desc: 'Violeta intenso sobre escuridão. Criativo e vibrante.',
    primary: '#a855f7',
    secondary: '#ec4899',
    bg: 'bg-[#0a0014]',
    border: 'border-purple-900/50',
    text: 'text-purple-50',
    accent: '#a855f7',
    preview: { bg: '#0a0014', card: '#150020', border: '#2d0050', pill: '#a855f7' },
  },
  {
    id: 'cyber_green',
    label: 'Cyber Green',
    emoji: '💻',
    category: 'Dark Premium',
    desc: 'Verde neon no terminal escuro. Hacker vibes puro.',
    primary: '#22c55e',
    secondary: '#16a34a',
    bg: 'bg-[#020c02]',
    border: 'border-green-900/40',
    text: 'text-green-50',
    accent: '#22c55e',
    preview: { bg: '#020c02', card: '#041204', border: '#0a2e0a', pill: '#22c55e' },
  },
  {
    id: 'deep_ocean',
    label: 'Deep Ocean',
    emoji: '🌊',
    category: 'Dark Premium',
    desc: 'Azul abissal com ciano pulsante. Profundo e imponente.',
    primary: '#06b6d4',
    secondary: '#0284c7',
    bg: 'bg-[#020918]',
    border: 'border-cyan-900/40',
    text: 'text-cyan-50',
    accent: '#06b6d4',
    preview: { bg: '#020918', card: '#04122a', border: '#082645', pill: '#06b6d4' },
  },
  {
    id: 'molten_iron',
    label: 'Molten Iron',
    emoji: '🔥',
    category: 'Dark Premium',
    desc: 'Laranja e âmbar incandescentes no fundo carvão.',
    primary: '#f97316',
    secondary: '#eab308',
    bg: 'bg-[#0f0900]',
    border: 'border-orange-900/50',
    text: 'text-orange-50',
    accent: '#f97316',
    preview: { bg: '#0f0900', card: '#1c1000', border: '#3d1f00', pill: '#f97316' },
  },
  {
    id: 'blood_red',
    label: 'Blood Red',
    emoji: '🩸',
    category: 'Dark Premium',
    desc: 'Vermelho crítico no escuridão total. Urgência e impacto.',
    primary: '#ef4444',
    secondary: '#dc2626',
    bg: 'bg-[#0a0000]',
    border: 'border-red-900/50',
    text: 'text-red-50',
    accent: '#ef4444',
    preview: { bg: '#0a0000', card: '#180000', border: '#3d0000', pill: '#ef4444' },
  },
  // ── GLASS / BLUR ──────────────────────────────
  {
    id: 'glacier_glass',
    label: 'Glacier Glass',
    emoji: '🧊',
    category: 'Glassmorphism',
    desc: 'Glassmorphism azul-gelo com blur profundo e reflexos.',
    primary: '#38bdf8',
    secondary: '#818cf8',
    bg: 'bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900',
    border: 'border-blue-400/20',
    text: 'text-blue-50',
    accent: '#38bdf8',
    preview: { bg: 'linear-gradient(135deg,#0f172a 0%,#1e1b4b 100%)', card: 'rgba(56,189,248,0.08)', border: 'rgba(56,189,248,0.2)', pill: '#38bdf8' },
  },
  {
    id: 'rose_quartz',
    label: 'Rose Quartz',
    emoji: '🌸',
    category: 'Glassmorphism',
    desc: 'Rosa suave e translúcido sobre gradiente magenta-vinho.',
    primary: '#f472b6',
    secondary: '#e879f9',
    bg: 'bg-gradient-to-br from-rose-950 via-fuchsia-950 to-slate-950',
    border: 'border-pink-400/20',
    text: 'text-pink-50',
    accent: '#f472b6',
    preview: { bg: 'linear-gradient(135deg,#4c0519 0%,#2e1065 100%)', card: 'rgba(244,114,182,0.08)', border: 'rgba(244,114,182,0.2)', pill: '#f472b6' },
  },
  {
    id: 'aurora_borealis',
    label: 'Aurora Borealis',
    emoji: '🌌',
    category: 'Glassmorphism',
    desc: 'Verde-azul mágico do norte. Gradiente de aurora e mística.',
    primary: '#34d399',
    secondary: '#60a5fa',
    bg: 'bg-gradient-to-br from-slate-950 via-teal-950 to-indigo-950',
    border: 'border-emerald-400/20',
    text: 'text-emerald-50',
    accent: '#34d399',
    preview: { bg: 'linear-gradient(135deg,#022c22 0%,#1e1b4b 100%)', card: 'rgba(52,211,153,0.07)', border: 'rgba(52,211,153,0.2)', pill: '#34d399' },
  },
  {
    id: 'sunset_dusk',
    label: 'Sunset Dusk',
    emoji: '🌅',
    category: 'Glassmorphism',
    desc: 'Crepúsculo laranja-roxo vibrante. Quente e envolvente.',
    primary: '#fb923c',
    secondary: '#c026d3',
    bg: 'bg-gradient-to-br from-orange-950 via-rose-950 to-purple-950',
    border: 'border-orange-400/20',
    text: 'text-orange-50',
    accent: '#fb923c',
    preview: { bg: 'linear-gradient(135deg,#431407 0%,#3b0764 100%)', card: 'rgba(251,146,60,0.08)', border: 'rgba(251,146,60,0.2)', pill: '#fb923c' },
  },
  // ── LIGHT / EDITORIAL ──────────────────────────
  {
    id: 'ivory_press',
    label: 'Ivory Press',
    emoji: '📰',
    category: 'Editorial Light',
    desc: 'Branco creme editorial. Tipografia serif imponente. Jornalismo clássico.',
    primary: '#1e293b',
    secondary: '#475569',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    text: 'text-slate-900',
    accent: '#1e293b',
    preview: { bg: '#fffbeb', card: '#ffffff', border: '#e2d9c5', pill: '#1e293b' },
  },
  {
    id: 'arctic_white',
    label: 'Arctic White',
    emoji: '❄️',
    category: 'Editorial Light',
    desc: 'Branco imaculado com azul ártico. SaaS premium limpo.',
    primary: '#2563eb',
    secondary: '#7c3aed',
    bg: 'bg-white',
    border: 'border-slate-200',
    text: 'text-slate-900',
    accent: '#2563eb',
    preview: { bg: '#f8fafc', card: '#ffffff', border: '#e2e8f0', pill: '#2563eb' },
  },
  {
    id: 'sage_leaf',
    label: 'Sage Leaf',
    emoji: '🌿',
    category: 'Editorial Light',
    desc: 'Verde sálvia orgânico. Sustentabilidade, bem-estar, natureza.',
    primary: '#059669',
    secondary: '#65a30d',
    bg: 'bg-green-50',
    border: 'border-green-200',
    text: 'text-green-950',
    accent: '#059669',
    preview: { bg: '#f0fdf4', card: '#ffffff', border: '#bbf7d0', pill: '#059669' },
  },
  {
    id: 'golden_press',
    label: 'Golden Press',
    emoji: '🏆',
    category: 'Editorial Light',
    desc: 'Âmbar e ouro sobre marfim. Premium, finanças e negócios.',
    primary: '#d97706',
    secondary: '#b45309',
    bg: 'bg-yellow-50',
    border: 'border-yellow-300',
    text: 'text-yellow-950',
    accent: '#d97706',
    preview: { bg: '#fffef0', card: '#ffffff', border: '#fde68a', pill: '#d97706' },
  },
  // ── CORPORATE / BRAND ──────────────────────────
  {
    id: 'slate_corporate',
    label: 'Slate Corporate',
    emoji: '🏢',
    category: 'Corporate',
    desc: 'Cinza ardósia profissional. Autoridade B2B e institucional.',
    primary: '#475569',
    secondary: '#334155',
    bg: 'bg-slate-100',
    border: 'border-slate-300',
    text: 'text-slate-900',
    accent: '#475569',
    preview: { bg: '#f1f5f9', card: '#ffffff', border: '#cbd5e1', pill: '#475569' },
  },
  {
    id: 'navy_trust',
    label: 'Navy Trust',
    emoji: '⚓',
    category: 'Corporate',
    desc: 'Azul marinho sólido. Confiança, finanças e tech enterprise.',
    primary: '#1d4ed8',
    secondary: '#1e40af',
    bg: 'bg-[#f0f4ff]',
    border: 'border-blue-200',
    text: 'text-blue-950',
    accent: '#1d4ed8',
    preview: { bg: '#eff6ff', card: '#ffffff', border: '#bfdbfe', pill: '#1d4ed8' },
  },
  {
    id: 'crimson_brand',
    label: 'Crimson Brand',
    emoji: '🎯',
    category: 'Corporate',
    desc: 'Vermelho carmesim ousado. Notícias, esportes, lifestyle.',
    primary: '#be123c',
    secondary: '#9f1239',
    bg: 'bg-rose-50',
    border: 'border-rose-200',
    text: 'text-rose-950',
    accent: '#be123c',
    preview: { bg: '#fff1f2', card: '#ffffff', border: '#fecdd3', pill: '#be123c' },
  },
  // ── RETRO / VINTAGE ──────────────────────────
  {
    id: 'retrowave',
    label: 'Retrowave',
    emoji: '📼',
    category: 'Retro / Criativo',
    desc: 'Synthwave anos 80. Magenta e ciano sobre preto absoluto.',
    primary: '#e879f9',
    secondary: '#22d3ee',
    bg: 'bg-[#050008]',
    border: 'border-fuchsia-900/50',
    text: 'text-fuchsia-50',
    accent: '#e879f9',
    preview: { bg: '#050008', card: '#100015', border: '#3d0050', pill: '#e879f9' },
  },
  {
    id: 'sepia_journal',
    label: 'Sepia Journal',
    emoji: '📜',
    category: 'Retro / Criativo',
    desc: 'Sépia envelhecida e vintage. Jornal clássico e nostálgico.',
    primary: '#92400e',
    secondary: '#78350f',
    bg: 'bg-[#fdf6e3]',
    border: 'border-amber-300',
    text: 'text-amber-950',
    accent: '#92400e',
    preview: { bg: '#fdf6e3', card: '#fef9ee', border: '#d4a96a', pill: '#92400e' },
  },
  {
    id: 'neon_city',
    label: 'Neon City',
    emoji: '🌃',
    category: 'Retro / Criativo',
    desc: 'Amarelo neon cyberpunk sobre asfalto molhado.',
    primary: '#facc15',
    secondary: '#f97316',
    bg: 'bg-[#030303]',
    border: 'border-yellow-900/40',
    text: 'text-yellow-50',
    accent: '#facc15',
    preview: { bg: '#030303', card: '#0a0a00', border: '#2a2600', pill: '#facc15' },
  },
];

const LAYOUT_PRESETS = [
  { id: 'classic_portal', label: '💎 Portal Clássico (Padrão Original)', desc: 'Hero central imponente + grade elegante + sidebar. O padrão original do ecossistema, em harmonia total com as matérias.' },
  { id: 'magazine_hero', label: '📰 Revista Magazine', desc: 'Hero cinematográfico 60vh + grid 3 col + sidebar. Ideal: Jornalismo, política, notícias.' },
  { id: 'stream_feed', label: '🎵 Stream Feed', desc: 'Banner de identidade + cards horizontais em feed contínuo. Ideal: Música, entretenimento.' },
  { id: 'mosaic_grid', label: '🎮 Mosaico Tech', desc: 'Hero duplo assimétrico + mosaico de cards variado. Ideal: Tech, games, esportes.' },
  { id: 'editorial_prose', label: '📖 Editorial Prosa', desc: 'Coluna única centralizada, serif literário, sem sidebar. Ideal: Literatura, histórias, viagem.' },
  { id: 'dashboard_portal', label: '📊 Dashboard Portal', desc: 'Sidenav fixo + KPIs + breaking news + grid compacto. Ideal: Finanças, crypto, dados.' },
  { id: 'video_cinema', label: '🎬 Cinema & Streaming', desc: 'Hero imersivo tipo Netflix/YouTube + cards 16:9 + dark mode. Ideal: Música, vídeo, trailers.' },
  { id: 'minimal_zen', label: '🧘 Minimal Zen', desc: 'Clean estilo Apple/Medium, sem cards pesados, foco total na leitura. Ideal: Filosofia, arquitetura, design.' },
  { id: 'cyber_terminal', label: '💻 Cyber Terminal', desc: 'Estilo terminal hacker, bordas neon, fonte mono, feed log de sistema. Ideal: Cripto, IA, programação.' },
];

const FONT_PRESETS = [
  { id: 'inter', label: 'Inter', desc: 'SaaS / Moderno / Universal', family: "'Inter', sans-serif" },
  { id: 'playfair', label: 'Playfair Display', desc: 'Jornalístico / Clássico / Imponente', family: "'Playfair Display', serif" },
  { id: 'dm_sans', label: 'DM Sans', desc: 'Editorial Limpo / Cultura / Pop', family: "'DM Sans', sans-serif" },
  { id: 'outfit', label: 'Outfit', desc: 'Tech / Games / Arrojado', family: "'Outfit', sans-serif" },
  { id: 'lora', label: 'Lora', desc: 'Literário / Histórias / Prosa', family: "'Lora', serif" },
  { id: 'space_grotesk', label: 'Space Grotesk', desc: 'Futurista / Cripto / Finanças', family: "'Space Grotesk', sans-serif" },
  { id: 'merriweather', label: 'Merriweather', desc: 'Jornal Impresso / Editorial Sólido', family: "'Merriweather', serif" },
  { id: 'jetbrains', label: 'JetBrains Mono', desc: 'Terminal / Dados / BI / Hack', family: "'JetBrains Mono', monospace" },
  { id: 'roboto', label: 'Roboto', desc: 'Neutro / Funcional / Direto', family: "'Roboto', sans-serif" },
  { id: 'syne', label: 'Syne', desc: 'Artístico / Design / Ousado', family: "'Syne', sans-serif" },
];

const ACCENT_STYLES = [
  { id: 'sharp', label: '◾ Sharp (Reto)', desc: 'Bordas técnicas (0px)', radius: '0px', pill: '0px' },
  { id: 'rounded', label: '🔲 Rounded (Suave)', desc: 'Bordas modernas (12px)', radius: '12px', pill: '8px' },
  { id: 'pill', label: '💊 Pill (Cápsula)', desc: 'Bordas fluidas (24px)', radius: '24px', pill: '9999px' },
];

const CATEGORIES = Array.from(new Set(THEME_PRESETS.map((t) => t.category)));

const parseFeatures = (val?: string): string[] => {
  try {
    const arr = JSON.parse(val || '["article","video_series","audio_track","photo_gallery","news_timeline"]');
    return Array.isArray(arr) ? arr : ["article","video_series","audio_track","photo_gallery","news_timeline"];
  } catch {
    return ["article","video_series","audio_track","photo_gallery","news_timeline"];
  }
};

const parseSocialLinks = (val?: string): Record<string, string> => {
  try {
    const obj = JSON.parse(val || '{}');
    return typeof obj === 'object' && obj !== null ? obj : {};
  } catch {
    return {};
  }
};

export default function AppearanceClient({ initialBlogs }: { initialBlogs: Blog[] }) {
  const [blogs, setBlogs] = useState<Blog[]>(initialBlogs);
  const [selectedBlogId, setSelectedBlogId] = useState<string>(initialBlogs[0]?.id || '');
  const [loading, setLoading] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [activeCategory, setActiveCategory] = useState<string>('Dark Premium');
  const [activeTab, setActiveTab] = useState<'themes' | 'typography' | 'branding' | 'modules' | 'social'>('themes');

  const currentBlog = blogs.find((b) => b.id === selectedBlogId) || blogs[0];

  const [form, setForm] = useState({
    name: currentBlog?.name || '',
    description: currentBlog?.description || '',
    theme: currentBlog?.theme || 'deep_ocean',
    primaryColor: currentBlog?.primaryColor || '#06b6d4',
    bgPrimary: currentBlog?.bgPrimary || '#020617',
    bgSurface: currentBlog?.bgSurface || '#1e293b',
    fontHeading: currentBlog?.fontHeading || 'Inter',
    fontBody: currentBlog?.fontBody || 'Inter',
    bannerUrl: currentBlog?.bannerUrl || '',
    secondaryColor: currentBlog?.secondaryColor || '#0284c7',
    layoutStyle: currentBlog?.layoutStyle || 'magazine_hero',
    fontFamily: currentBlog?.fontFamily || 'inter',
    logoUrl: currentBlog?.logoUrl || '',
    accentStyle: currentBlog?.accentStyle || 'rounded',
    activeFeatures: parseFeatures(currentBlog?.activeFeatures),
    socialLinks: parseSocialLinks(currentBlog?.socialLinks),
  });

  const activeTheme = THEME_PRESETS.find((t) => t.id === form.theme) || THEME_PRESETS[3];
  const activeFont = FONT_PRESETS.find((f) => f.id === form.fontFamily) || FONT_PRESETS[0];
  const activeAccent = ACCENT_STYLES.find((a) => a.id === form.accentStyle) || ACCENT_STYLES[1];

  const handleSelectBlog = (blog: Blog) => {
    setSelectedBlogId(blog.id);
    setForm({
      name: blog.name || '',
      description: blog.description || '',
      theme: blog.theme || 'deep_ocean',
      primaryColor: blog.primaryColor || '#06b6d4',
      bgPrimary: blog.bgPrimary || '#020617',
      bgSurface: blog.bgSurface || '#1e293b',
      fontHeading: blog.fontHeading || 'Inter',
      fontBody: blog.fontBody || 'Inter',
      bannerUrl: blog.bannerUrl || '',
      secondaryColor: blog.secondaryColor || '#0284c7',
      layoutStyle: blog.layoutStyle || 'magazine_hero',
      fontFamily: blog.fontFamily || 'inter',
      logoUrl: blog.logoUrl || '',
      accentStyle: blog.accentStyle || 'rounded',
      activeFeatures: parseFeatures(blog.activeFeatures),
      socialLinks: parseSocialLinks(blog.socialLinks),
    });
  };

  const applyPreset = (preset: typeof THEME_PRESETS[0]) => {
    setForm((f) => ({ ...f, theme: preset.id, primaryColor: preset.primary, secondaryColor: preset.secondary }));
  };

  const showToast = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 5000);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentBlog) return;
    setLoading(true);
    setNotification(null);
    try {
      const formData = new FormData();
      formData.append('blogId', currentBlog.id);
      formData.append('name', form.name);
      formData.append('description', form.description);
      formData.append('theme', form.theme);
      formData.append('primaryColor', form.primaryColor);
      formData.append('secondaryColor', form.secondaryColor);
      formData.append('bgPrimary', form.bgPrimary);
      formData.append('bgSurface', form.bgSurface);
      formData.append('fontHeading', form.fontHeading);
      formData.append('fontBody', form.fontBody);
      formData.append('bannerUrl', form.bannerUrl);
      formData.append('layoutStyle', form.layoutStyle);
      formData.append('fontFamily', form.fontFamily);
      formData.append('logoUrl', form.logoUrl);
      formData.append('accentStyle', form.accentStyle);
      formData.append('activeFeatures', JSON.stringify(form.activeFeatures));
      formData.append('socialLinks', JSON.stringify(form.socialLinks));

      const res = await saveAppearance(formData);
      if (res.success) {
        setBlogs((prev) =>
          prev.map((b) =>
            b.id === currentBlog.id
              ? {
                  ...b,
                  name: form.name,
                  description: form.description,
                  theme: form.theme,
                  primaryColor: form.primaryColor,
                  secondaryColor: form.secondaryColor,
                  layoutStyle: form.layoutStyle,
                  fontFamily: form.fontFamily,
                  logoUrl: form.logoUrl,
                  accentStyle: form.accentStyle,
                  activeFeatures: JSON.stringify(form.activeFeatures),
                  socialLinks: JSON.stringify(form.socialLinks),
                }
              : b
          )
        );
        showToast('success', `✨ Identidade visual "${form.name}" — tema "${activeTheme.label}" salvo com sucesso!`);
      } else {
        showToast('error', res.error || 'Erro ao salvar modificações.');
      }
    } catch {
      showToast('error', 'Erro de conexão com o banco de dados.');
    } finally {
      setLoading(false);
    }
  };

  if (!currentBlog) {
    return (
      <div className="py-24 text-center text-slate-500 bg-slate-900/60 backdrop-blur-xl rounded-3xl border border-slate-800">
        <span className="text-4xl mb-4 block">🎨</span>
        <p className="font-bold text-slate-300">Nenhum veículo registrado na frota.</p>
      </div>
    );
  }

  const pvBg = typeof activeTheme.preview.bg === 'string' && activeTheme.preview.bg.startsWith('linear')
    ? { background: activeTheme.preview.bg }
    : { backgroundColor: activeTheme.preview.bg };

  const isLight = activeTheme.category.includes('Light') || activeTheme.category.includes('Corporate');

  return (
    <div className="max-w-[1440px] mx-auto space-y-8 pb-16 animate-in fade-in duration-500">
      {/* Google Fonts link injetado dinamicamente para o preview funcionar perfeitamente */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;700&family=Inter:wght@400;700;900&family=JetBrains+Mono:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&family=Merriweather:wght@400;700;900&family=Outfit:wght@400;700&family=Playfair+Display:wght@700;900&family=Roboto:wght@400;700&family=Space+Grotesk:wght@500;700;900&family=Syne:wght@700;800&display=swap');
      `}</style>

      {/* TOAST */}
      {notification && (
        <div className={`p-4 rounded-2xl border flex items-center justify-between shadow-xl transition-all ${notification.type === 'success' ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300' : 'bg-red-950/80 border-red-500/40 text-red-300'}`}>
          <div className="flex items-center gap-3 text-xs font-semibold">
            <span>{notification.type === 'success' ? '✓' : '⚠️'}</span>
            <span>{notification.message}</span>
          </div>
          <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white text-xs font-bold px-2">✕</button>
        </div>
      )}

      {/* HEADER */}
      <div className="bg-[#050012]/90 backdrop-blur-2xl p-8 md:p-10 rounded-3xl border border-purple-900/50 shadow-2xl relative overflow-hidden flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div className="absolute top-0 right-0 w-96 h-96 rounded-full blur-3xl pointer-events-none -mr-32 -mt-32 transition-all" style={{ backgroundColor: `${form.primaryColor}18` }} />
        <div className="space-y-3 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-semibold tracking-wide" style={{ backgroundColor: `${form.primaryColor}15`, borderColor: `${form.primaryColor}30`, color: form.primaryColor }}>
            <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: form.primaryColor }} />
            ESTÚDIO VISUAL ARCHITECTURE • {THEME_PRESETS.length} TEMAS • {LAYOUT_PRESETS.length} PADRÕES DE LAYOUT • {FONT_PRESETS.length} FONTES
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 via-yellow-500 to-purple-400 tracking-tight">
            Estúdio de Identidade Visual Multi-Portal
          </h1>
          <p className="text-slate-400 text-sm md:text-base max-w-2xl font-normal leading-relaxed">
            Personalize o Canvas (UX), cores, tipografia e logomarcas. O motor backend (IA, SEO, ads, RSS) opera <strong>100% idêntico</strong> em todos os layouts escolhidos.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <Link href="/admin" className="px-5 py-3 rounded-xl bg-slate-900/80 hover:bg-slate-800 text-xs font-bold text-slate-300 hover:text-white transition-colors border border-slate-700/80 shadow-sm flex items-center gap-2">
            ← Painel Central
          </Link>
          <a href={`https://${currentBlog.domain}`} target="_blank" rel="noopener noreferrer" className="px-6 py-3 rounded-xl text-xs font-bold text-white transition-all shadow-lg flex items-center gap-2" style={{ backgroundColor: form.primaryColor }}>
            Ver Vitrine ↗
          </a>
        </div>
      </div>

      {/* SELETOR DE PORTAIS */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 no-scrollbar">
        {blogs.map((blog) => {
          const isSelected = blog.id === currentBlog.id;
          const blogTheme = THEME_PRESETS.find((t) => t.id === blog.theme) || THEME_PRESETS[3];
          return (
            <button
              key={blog.id}
              onClick={() => handleSelectBlog(blog)}
              className={`px-5 py-3 rounded-2xl text-xs font-extrabold transition-all flex items-center gap-2.5 shrink-0 border ${isSelected ? 'text-white shadow-lg' : 'bg-slate-900/80 hover:bg-slate-800 text-slate-400 hover:text-white border-slate-800'}`}
              style={isSelected ? { background: `linear-gradient(135deg, ${blogTheme.primary}cc, ${blogTheme.secondary}99)`, borderColor: blogTheme.primary } : {}}
            >
              <span>{blogTheme.emoji}</span>
              <span>{blog.name}</span>
              <span className="text-[10px] font-mono opacity-50">({blog.domain})</span>
            </button>
          );
        })}
      </div>

      {/* GRID PRINCIPAL */}
      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">

        {/* COLUNA ESQUERDA: FORMULÁRIO COMPLETO (5 col) */}
        <div className="xl:col-span-5 space-y-6">

          <form onSubmit={handleSubmit} className="bg-slate-900/60 backdrop-blur-xl p-6 md:p-8 rounded-3xl border border-slate-800/80 shadow-xl space-y-6">
            
            {/* TABS DE CONFIGURAÇÃO */}
            <div className="flex border-b border-slate-800 pb-2 gap-1">
              <button
                type="button"
                onClick={() => setActiveTab('themes')}
                className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${activeTab === 'themes' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                style={activeTab === 'themes' ? { color: form.primaryColor, borderBottom: `2px solid ${form.primaryColor}` } : {}}
              >
                <span>🎨</span>
                <span>Layout & Cores</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('typography')}
                className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${activeTab === 'typography' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                style={activeTab === 'typography' ? { color: form.primaryColor, borderBottom: `2px solid ${form.primaryColor}` } : {}}
              >
                <span>🔤</span>
                <span>Tipografia</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('branding')}
                className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${activeTab === 'branding' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                style={activeTab === 'branding' ? { color: form.primaryColor, borderBottom: `2px solid ${form.primaryColor}` } : {}}
              >
                <span>🏷️</span>
                <span>Marca & Bordas</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('modules')}
                className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${activeTab === 'modules' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                style={activeTab === 'modules' ? { color: form.primaryColor, borderBottom: `2px solid ${form.primaryColor}` } : {}}
              >
                <span>⚡</span>
                <span>Módulos & IA</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('social')}
                className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${activeTab === 'social' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
                style={activeTab === 'social' ? { color: form.primaryColor, borderBottom: `2px solid ${form.primaryColor}` } : {}}
              >
                <span>🌐</span>
                <span>Redes & Links</span>
              </button>
            </div>

            {/* CONTEÚDO ABA 1: LAYOUT & CORES */}
            {activeTab === 'themes' && (
              <div className="space-y-5 animate-in fade-in duration-300">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Nome Exibido na Vitrine</label>
                  <input type="text" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-bold text-white focus:outline-none transition-all" style={{ borderColor: form.name ? `${form.primaryColor}40` : undefined }} required />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Descrição / Slogan SEO</label>
                  <textarea rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-slate-300 focus:outline-none transition-all leading-relaxed" placeholder="Ex: O melhor blog financeiro autônomo da rede." />
                </div>

                {/* ESTRUTURA DE LAYOUT */}
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Padrão de Design (Canvas UX)</label>
                  <div className="space-y-2">
                    {LAYOUT_PRESETS.map((lp) => (
                      <button
                        key={lp.id}
                        type="button"
                        onClick={() => setForm({ ...form, layoutStyle: lp.id })}
                        className={`w-full p-3.5 rounded-xl border text-left transition-all flex items-start gap-3 ${form.layoutStyle === lp.id ? 'text-white border-opacity-80 shadow-md' : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'}`}
                        style={form.layoutStyle === lp.id ? { backgroundColor: `${form.primaryColor}15`, borderColor: form.primaryColor, color: form.primaryColor } : {}}
                      >
                        <div className="w-4 h-4 mt-0.5 rounded-full border-2 flex items-center justify-center shrink-0" style={{ borderColor: form.layoutStyle === lp.id ? form.primaryColor : '#475569' }}>
                          {form.layoutStyle === lp.id && <div className="w-2 h-2 rounded-full" style={{ backgroundColor: form.primaryColor }} />}
                        </div>
                        <div>
                          <div className="text-xs font-black leading-tight text-white">{lp.label}</div>
                          <div className="text-[10px] text-slate-400 mt-1 leading-normal">{lp.desc}</div>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* MOTOR DE CORES AVANÇADO (V3) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
                  <div className="bg-[#150a21] p-3.5 rounded-2xl border border-purple-900/50">
                    <label className="block text-[11px] font-bold text-purple-300 uppercase tracking-wider mb-2">Fundo Mestre (bgPrimary)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.bgPrimary} onChange={(e) => setForm({ ...form, bgPrimary: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.bgPrimary} onChange={(e) => setForm({ ...form, bgPrimary: e.target.value })} className="w-full bg-black border border-purple-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#150a21] p-3.5 rounded-2xl border border-purple-900/50">
                    <label className="block text-[11px] font-bold text-purple-300 uppercase tracking-wider mb-2">Fundo Conteúdo (bgSurface)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.bgSurface} onChange={(e) => setForm({ ...form, bgSurface: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.bgSurface} onChange={(e) => setForm({ ...form, bgSurface: e.target.value })} className="w-full bg-black border border-purple-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#1a1405] p-3.5 rounded-2xl border border-yellow-900/50">
                    <label className="block text-[11px] font-bold text-yellow-500 uppercase tracking-wider mb-2">Cor Primária (Accent)</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.primaryColor} onChange={(e) => setForm({ ...form, primaryColor: e.target.value })} className="w-full bg-black border border-yellow-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                  <div className="bg-[#1a1405] p-3.5 rounded-2xl border border-yellow-900/50">
                    <label className="block text-[11px] font-bold text-yellow-500 uppercase tracking-wider mb-2">Cor Secundária</label>
                    <div className="flex items-center gap-2">
                      <input type="color" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-8 h-8 rounded-lg bg-transparent cursor-pointer border-0" />
                      <input type="text" value={form.secondaryColor} onChange={(e) => setForm({ ...form, secondaryColor: e.target.value })} className="w-full bg-black border border-yellow-900 rounded-lg px-2 py-1 text-xs font-mono text-white focus:outline-none" />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* CONTEÚDO ABA 2: TIPOGRAFIA */}
            {activeTab === 'typography' && (
              <div className="space-y-4 animate-in fade-in duration-300">
                <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 mb-4">
                  <p className="text-xs text-slate-400 leading-relaxed">
                    A tipografia muda a percepção de autoridade do site. Fontes serifadas transmitem tradição editorial e jornalismo; fontes sans-serif modernas transmitem inovação e agilidade.
                  </p>
                </div>

                <div className="space-y-4 bg-gradient-to-br from-black to-[#0a0514] p-5 rounded-2xl border border-purple-500/20 shadow-xl">
                  <div className="bg-purple-900/20 text-purple-300 p-3 rounded-xl border border-purple-800/30 text-xs">
                    💡 <strong>Motor V3:</strong> Insira os nomes exatos do <em>Google Fonts</em>. O sistema irá importar dinamicamente (Ex: "Space Grotesk", "DM Serif Display").
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2">Fonte dos Títulos (Heading)</label>
                    <input type="text" value={form.fontHeading} onChange={(e) => setForm({ ...form, fontHeading: e.target.value })} className="w-full bg-black border border-purple-900/50 rounded-xl p-3 text-sm font-bold text-white focus:outline-none focus:border-purple-500 transition-all" placeholder="Ex: Playfair Display" />
                  </div>
                  
                  <div>
                    <label className="block text-xs font-bold text-yellow-500 uppercase tracking-wider mb-2">Fonte do Corpo (Body)</label>
                    <input type="text" value={form.fontBody} onChange={(e) => setForm({ ...form, fontBody: e.target.value })} className="w-full bg-black border border-purple-900/50 rounded-xl p-3 text-sm text-white focus:outline-none focus:border-purple-500 transition-all" placeholder="Ex: Inter" />
                  </div>
                </div>
              </div>
            )}

            {/* CONTEÚDO ABA 3: MARCA & BORDAS */}
            {activeTab === 'branding' && (
              <div className="space-y-5 animate-in fade-in duration-300">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">URL da Logomarca Personalizada (Opcional)</label>
                  <input type="url" value={form.logoUrl} onChange={(e) => setForm({ ...form, logoUrl: e.target.value })} className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs font-mono text-slate-200 focus:outline-none transition-all placeholder:text-slate-600" placeholder="https://exemplo.com/logo.png" />
                  <p className="text-[10px] text-slate-500 mt-1.5">Deixe em branco para usar o ícone gerado com a inicial do portal e o gradiente do tema.</p>
                </div>

                {form.logoUrl && (
                  <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center gap-4">
                    <span className="text-[10px] font-bold uppercase text-slate-500">Preview Logo:</span>
                    <img src={form.logoUrl} alt="Logo" className="max-h-12 max-w-[180px] object-contain" />
                  </div>
                )}

                <div className="pt-2">
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Estilo de Acento e Bordas (Radius)</label>
                  <div className="grid grid-cols-1 gap-2.5">
                    {ACCENT_STYLES.map((ac) => (
                      <button
                        key={ac.id}
                        type="button"
                        onClick={() => setForm({ ...form, accentStyle: ac.id })}
                        className={`w-full p-3.5 border text-left transition-all flex items-center justify-between ${form.accentStyle === ac.id ? 'bg-slate-950 text-white shadow-md' : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'}`}
                        style={{
                          borderRadius: ac.radius,
                          borderColor: form.accentStyle === ac.id ? form.primaryColor : undefined,
                          boxShadow: form.accentStyle === ac.id ? `0 0 15px ${form.primaryColor}15` : undefined
                        }}
                      >
                        <div>
                          <div className="text-xs font-extrabold text-white">{ac.label}</div>
                          <div className="text-[10px] text-slate-500 mt-0.5">{ac.desc}</div>
                        </div>
                        <div className="w-12 h-6 border-2 flex items-center justify-center text-[9px] font-bold uppercase" style={{ borderRadius: ac.pill, borderColor: form.primaryColor, color: form.primaryColor }}>
                          Pill
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* CONTEÚDO ABA 4: MÓDULOS & IA */}
            {activeTab === 'modules' && (
              <div className="space-y-5 animate-in fade-in duration-300">
                <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                  <span className="font-extrabold text-white block mb-1">🤖 Inteligência de Conteúdo & Interatividade</span>
                  Configure quais módulos interativos estão ativos para este portal. A IA Redatora (auto-writer) priorizará esses formatos, e o frontend exibirá players e timelines dedicadas nas matérias.
                </div>

                <div className="space-y-2.5">
                  {[
                    { id: 'audio_track', label: '🎧 Módulo de Áudio & Podcast', desc: 'Player de ondas animado com progresso interativo e playlist editorial (Música/Entrevistas).' },
                    { id: 'video_series', label: '🎬 Série de Vídeo em Episódios', desc: 'Player central com lista lateral navegável de capítulos (Séries/Tutoriais/Aulas).' },
                    { id: 'photo_gallery', label: '📸 Galeria de Imagens Editorial', desc: 'Grade mosaico responsiva com legendas dinâmicas e ampliação Lightbox sem diálogos nativos.' },
                    { id: 'news_timeline', label: '⏱️ Linha do Tempo Cronológica', desc: 'Nós interativos conectados mostrando a correlação e evolução de fatos jornalísticos.' }
                  ].map((mod) => {
                    const isChecked = form.activeFeatures.includes(mod.id);
                    return (
                      <div
                        key={mod.id}
                        onClick={() => {
                          const next = isChecked 
                            ? form.activeFeatures.filter(f => f !== mod.id)
                            : [...form.activeFeatures, mod.id];
                          setForm({ ...form, activeFeatures: next });
                        }}
                        className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start justify-between gap-4 ${
                          isChecked ? 'bg-slate-950/90 text-white shadow-md' : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-white'
                        }`}
                        style={{
                          borderColor: isChecked ? `${form.primaryColor}80` : undefined,
                          borderRadius: activeAccent.radius
                        }}
                      >
                        <div className="flex-1">
                          <div className="text-xs font-bold flex items-center gap-2">
                            <span>{mod.label}</span>
                            {isChecked && <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-mono" style={{ backgroundColor: `${form.primaryColor}20`, color: form.primaryColor }}>Ativo para IA</span>}
                          </div>
                          <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">{mod.desc}</p>
                        </div>
                        <div 
                          className={`w-5 h-5 rounded flex items-center justify-center text-xs font-bold transition-all shrink-0 ${
                            isChecked ? 'text-white' : 'border border-slate-700 bg-slate-900'
                          }`}
                          style={isChecked ? { backgroundColor: form.primaryColor } : {}}
                        >
                          {isChecked ? '✓' : ''}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* CONTEÚDO ABA 5: REDES SOCIAIS & NEWSLETTER */}
            {activeTab === 'social' && (
              <div className="space-y-4 animate-in fade-in duration-300">
                <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800/80 text-xs text-slate-300 leading-relaxed">
                  <span className="font-extrabold text-white block mb-1">🌐 Hub Social & Canais Conectados</span>
                  Insira os links dos canais sociais deste portal. O componente interativo no rodapé e nas matérias direcionará o fluxo de usuários diretamente para essas 8 redes sociais e newsletter!
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-[380px] overflow-y-auto pr-1">
                  {[
                    { key: 'youtube', label: '📺 YouTube (Vídeos / Shorts)', placeholder: 'https://youtube.com/@seucanal' },
                    { key: 'facebook', label: '👥 Facebook (Página / Comunidade)', placeholder: 'https://facebook.com/seucanal' },
                    { key: 'instagram', label: '📸 Instagram (Feed / Reels)', placeholder: 'https://instagram.com/seucanal' },
                    { key: 'twitter', label: '🐦 Twitter / X (Notícias em Tempo Real)', placeholder: 'https://x.com/seucanal' },
                    { key: 'tiktok', label: '🎵 TikTok (Vídeos Curtos Virais)', placeholder: 'https://tiktok.com/@seucanal' },
                    { key: 'kwai', label: '⚡ Kwai (Vídeos & Engajamento)', placeholder: 'https://kwai.com/@seucanal' },
                    { key: 'dailymotion', label: '🎬 Dailymotion (Canal de Vídeos HD)', placeholder: 'https://dailymotion.com/seucanal' },
                    { key: 'newsletter', label: '✉️ Newsletter (Link ou #subscribe)', placeholder: '#subscribe ou URL de inscrição' },
                  ].map((field) => (
                    <div key={field.key}>
                      <label className="block text-[11px] font-bold text-slate-400 mb-1">{field.label}</label>
                      <input
                        type="text"
                        value={form.socialLinks[field.key] || ''}
                        onChange={(e) => setForm({
                          ...form,
                          socialLinks: { ...form.socialLinks, [field.key]: e.target.value }
                        })}
                        placeholder={field.placeholder}
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-xs text-white placeholder-slate-600 focus:outline-none transition-all font-mono"
                        style={{ borderColor: form.socialLinks[field.key] ? `${form.primaryColor}50` : undefined }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* BOTÕES DE SALVAMENTO */}
            <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row gap-3">
              <button
                type="button"
                onClick={() => { applyPreset(THEME_PRESETS[3]); setForm((f) => ({ ...f, layoutStyle: 'classic_portal', fontFamily: 'inter', accentStyle: 'rounded' })); showToast('success', '✨ Padrão Original (Portal Clássico) restaurado!'); }}
                className="px-5 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 hover:text-white transition-all cursor-pointer"
              >
                🔄 Resetar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 py-3.5 rounded-xl text-xs font-extrabold text-white transition-all shadow-lg disabled:opacity-50 flex items-center justify-center gap-2 active:scale-95 cursor-pointer"
                style={{ background: `linear-gradient(135deg, ${form.primaryColor}, ${form.secondaryColor})`, borderRadius: activeAccent.radius }}
              >
                {loading ? <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> : <span>✨ Salvar no Banco SQLite</span>}
              </button>
            </div>
          </form>
        </div>

        {/* COLUNA DIREITA: GALERIA DE TEMAS + SIMULADOR REAL DO LAYOUT (7 col) */}
        <div className="xl:col-span-7 space-y-6">

          {/* GALERIA DE TEMAS */}
          <div className="bg-slate-900/60 backdrop-blur-xl p-6 rounded-3xl border border-slate-800/80 shadow-xl">
            <div className="flex justify-between items-center pb-4 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-base font-extrabold text-white">Paletas & Temas de Cores</h3>
                <p className="text-xs text-slate-500 mt-0.5">As cores são aplicadas sobre o padrão de layout selecionado</p>
              </div>
              <div className="flex gap-1.5 flex-wrap">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`px-3 py-1.5 rounded-lg text-[11px] font-bold transition-all ${activeCategory === cat ? 'text-white' : 'bg-slate-950/60 border border-slate-800 text-slate-500 hover:text-white'}`}
                    style={activeCategory === cat ? { background: `linear-gradient(135deg, ${form.primaryColor}cc, ${form.secondaryColor}99)` } : {}}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-[260px] overflow-y-auto pr-1">
              {THEME_PRESETS.filter((t) => t.category === activeCategory).map((preset) => {
                const isActive = form.theme === preset.id;
                return (
                  <button
                    key={preset.id}
                    onClick={() => applyPreset(preset)}
                    className={`relative p-3.5 rounded-2xl border text-left transition-all hover:scale-[1.03] active:scale-95 group overflow-hidden ${isActive ? 'ring-2 shadow-xl scale-[1.02]' : 'border-slate-800 hover:border-slate-700'}`}
                    style={
                      isActive
                        ? { borderColor: preset.primary, outline: `2px solid ${preset.primary}`, boxShadow: `0 0 20px ${preset.primary}30`, borderRadius: activeAccent.radius } as React.CSSProperties
                        : { borderRadius: activeAccent.radius } as React.CSSProperties
                    }
                  >
                    {/* Miniatura de preview */}
                    <div
                      className="w-full h-12 rounded-xl mb-2.5 overflow-hidden relative flex flex-col justify-between p-2"
                      style={typeof preset.preview.bg === 'string' && preset.preview.bg.startsWith('linear')
                        ? { background: preset.preview.bg }
                        : { backgroundColor: preset.preview.bg }}
                    >
                      <div className="flex items-center gap-1.5">
                        <div className="w-3 h-3 rounded" style={{ backgroundColor: preset.primary }} />
                        <div className="h-1 w-10 rounded-full" style={{ backgroundColor: preset.primary, opacity: 0.6 }} />
                      </div>
                      <div className="rounded p-1" style={{ backgroundColor: preset.preview.card, border: `1px solid ${preset.preview.border}` }}>
                        <div className="h-0.5 w-6 rounded mb-0.5" style={{ backgroundColor: preset.preview.pill, opacity: 0.7 }} />
                      </div>
                    </div>

                    <div className="flex items-center gap-1.5 mb-1">
                      <span className="text-sm">{preset.emoji}</span>
                      <span className="text-xs font-extrabold text-white leading-tight truncate">{preset.label}</span>
                    </div>
                    
                    <div className="flex gap-1 mt-1.5">
                      <div className="w-3.5 h-3.5 rounded-full border border-slate-800" style={{ backgroundColor: preset.primary }} />
                      <div className="w-3.5 h-3.5 rounded-full border border-slate-800" style={{ backgroundColor: preset.secondary }} />
                    </div>

                    {isActive && (
                      <div className="absolute top-2 right-2 w-4 h-4 rounded-full flex items-center justify-center text-white text-[8px] font-black" style={{ backgroundColor: preset.primary }}>
                        ✓
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* SIMULADOR AO VIVO DO LAYOUT SELECIONADO */}
          <div className="bg-slate-900/60 backdrop-blur-xl p-5 rounded-3xl border border-slate-800/80 shadow-xl">
            <div className="flex justify-between items-center pb-3 border-b border-slate-800 mb-4">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full animate-pulse" style={{ backgroundColor: form.primaryColor }} />
                <span className="text-xs font-extrabold text-white uppercase tracking-wider">
                  Simulador Live — {LAYOUT_PRESETS.find((l) => l.id === form.layoutStyle)?.label || form.layoutStyle}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-mono text-slate-400 px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
                  Fonte: {activeFont.label}
                </span>
                <span className="text-[10px] font-mono text-slate-400 px-2 py-0.5 rounded bg-slate-950 border border-slate-800">
                  Borda: {activeAccent.label.split(' ')[1]}
                </span>
              </div>
            </div>

            {/* CAIXA DO PREVIEW DINÂMICO REAL */}
            <div
              className="border-4 p-5 md:p-6 transition-all relative overflow-hidden flex flex-col justify-between shadow-2xl min-h-[400px]"
              style={{
                ...pvBg,
                borderColor: `${form.primaryColor}40`,
                borderRadius: activeAccent.radius,
                fontFamily: activeFont.family
              }}
            >
              {/* Glows */}
              <div className="absolute top-0 right-0 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none -mr-12 -mt-12 transition-all" style={{ backgroundColor: form.primaryColor }} />
              <div className="absolute bottom-0 left-0 w-48 h-48 rounded-full blur-3xl opacity-15 pointer-events-none -ml-12 -mb-12 transition-all" style={{ backgroundColor: form.secondaryColor }} />

              {/* ── PREVIEW 0: CLASSIC PORTAL (O Padrão Original) ── */}
              {form.layoutStyle === 'classic_portal' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between">
                  {/* Navbar Executiva */}
                  <div className="flex justify-between items-center pb-3 border-b" style={{ borderColor: `${form.primaryColor}30` }}>
                    <div className="flex items-center gap-2.5">
                      {form.logoUrl ? (
                        <img src={form.logoUrl} alt="Logo" className="h-7 max-w-[120px] object-contain" />
                      ) : (
                        <div className="w-8 h-8 rounded flex items-center justify-center font-black text-white text-xs shadow-md" style={{ background: `linear-gradient(135deg, ${form.primaryColor}, ${form.secondaryColor})`, borderRadius: activeAccent.radius }}>
                          {form.name ? form.name.slice(0, 1).toUpperCase() : 'P'}
                        </div>
                      )}
                      <span className="font-extrabold text-sm tracking-tight uppercase" style={{ color: isLight ? '#0f172a' : 'white' }}>{form.name || 'Portal Clássico'}</span>
                    </div>
                    <div className="flex gap-2 text-[9px] font-extrabold uppercase tracking-widest text-slate-400">
                      <span>Notícias</span><span>•</span><span>Análise</span><span>•</span><span>IA</span>
                    </div>
                  </div>

                  {/* Hero Central Imponente */}
                  <div className="p-5 rounded-2xl relative overflow-hidden border shadow-xl flex flex-col justify-end min-h-[160px]" style={{ background: `linear-gradient(135deg, #0f172a 0%, ${form.primaryColor}30 100%)`, borderColor: `${form.primaryColor}50`, borderRadius: activeAccent.radius }}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2.5 py-0.5 text-[8px] font-black uppercase tracking-widest text-white shadow" style={{ backgroundColor: form.primaryColor, borderRadius: activeAccent.pill }}>
                        🔥 Em Destaque
                      </span>
                      <span className="text-[9px] text-slate-300 font-mono">Há 10 min</span>
                    </div>
                    <h2 className="text-base font-black leading-snug text-white mb-1">
                      IA Editorial revoluciona a criação autônoma de portais multimídia em tempo real
                    </h2>
                    <p className="text-[10px] text-slate-300 leading-relaxed line-clamp-2">
                      {form.description || 'O ecossistema colmeia integra relatórios, tendências e publicação contínua sem intervenção humana.'}
                    </p>
                  </div>

                  {/* Grid 2 colunas elegante */}
                  <div className="grid grid-cols-2 gap-3 pt-1">
                    {[1, 2].map((i) => (
                      <div key={i} className="p-3 border transition-all shadow-sm hover:shadow-md flex flex-col justify-between" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                        <div>
                          <div className="text-[8px] font-bold uppercase tracking-wider mb-1" style={{ color: form.primaryColor }}>Artigo • Análise</div>
                          <div className="text-[11px] font-extrabold leading-snug mb-1.5" style={{ color: isLight ? '#0f172a' : 'white' }}>O futuro do jornalismo sintético de precisão</div>
                        </div>
                        <div className="flex justify-between items-center text-[8px] opacity-60 font-mono pt-2 border-t border-current/10">
                          <span>⏱️ 3 min</span>
                          <span style={{ color: form.primaryColor }}>Ler →</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── PREVIEW 1: MAGAZINE HERO (Jornalismo/Notícias) ── */}
              {form.layoutStyle === 'magazine_hero' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between">
                  {/* Navbar */}
                  <div className="flex justify-between items-center pb-3 border-b" style={{ borderColor: `${form.primaryColor}25` }}>
                    <div className="flex items-center gap-2.5">
                      {form.logoUrl ? (
                        <img src={form.logoUrl} alt="Logo" className="h-7 max-w-[120px] object-contain" />
                      ) : (
                        <div className="w-8 h-8 rounded flex items-center justify-center font-black text-white text-xs shadow" style={{ backgroundColor: form.primaryColor, borderRadius: activeAccent.radius }}>
                          {form.name ? form.name.slice(0, 1).toUpperCase() : 'M'}
                        </div>
                      )}
                      <span className="font-black text-sm uppercase tracking-tight" style={{ color: isLight ? '#1e293b' : 'white' }}>{form.name || 'Portal Magazine'}</span>
                    </div>
                    <div className="flex gap-2 text-[9px] font-bold uppercase tracking-wider" style={{ color: isLight ? '#475569' : '#94a3b8' }}>
                      <span>Política</span><span>•</span><span>Economia</span><span>•</span><span>Mundo</span>
                    </div>
                  </div>

                  {/* Hero Cinematográfico Simulado */}
                  <div className="p-5 rounded-xl relative overflow-hidden border shadow-lg" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                    <div className="inline-block px-2 py-0.5 text-[8px] font-black uppercase tracking-widest text-white mb-2" style={{ backgroundColor: form.primaryColor, borderRadius: activeAccent.pill }}>
                      📌 Manchete Principal
                    </div>
                    <h2 className="text-base font-black leading-snug mb-1.5" style={{ color: isLight ? '#0f172a' : 'white' }}>
                      Inteligência Artificial revoluciona a cobertura autônoma de notícias 24/7
                    </h2>
                    <p className="text-[10px] leading-relaxed mb-3 opacity-70" style={{ color: isLight ? '#334155' : '#cbd5e1' }}>
                      {form.description || 'Uma análise profunda sobre os novos algoritmos de síntese neural que produzem jornalismo em tempo real sem falhas.'}
                    </p>
                    <div className="flex items-center gap-2 text-[9px] font-bold opacity-60">
                      <span>Por Redação Neural</span><span>•</span><span>Há 15 min</span>
                    </div>
                  </div>

                  {/* Grid 3 colunas simulado */}
                  <div className="grid grid-cols-3 gap-2.5 pt-1">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="p-2.5 border transition-all" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                        <div className="w-8 h-1 rounded mb-1.5" style={{ backgroundColor: form.secondaryColor }} />
                        <div className="h-2.5 w-full rounded mb-1 bg-current/20" />
                        <div className="h-2 w-3/4 rounded bg-current/10" />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── PREVIEW 2: STREAM FEED (Música/Cultura) ── */}
              {form.layoutStyle === 'stream_feed' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between">
                  {/* Navbar Minimalista */}
                  <div className="flex justify-between items-center pb-2 border-b" style={{ borderColor: `${form.primaryColor}20` }}>
                    <span className="font-black text-base uppercase tracking-tighter" style={{ color: isLight ? '#0f172a' : 'white' }}>{form.name || 'Stream Editorial'}</span>
                    <span className="text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 border" style={{ color: form.primaryColor, borderColor: `${form.primaryColor}40`, borderRadius: activeAccent.pill }}>
                      {currentBlog.niche || 'Música & Cultura'}
                    </span>
                  </div>

                  {/* Banner Identidade */}
                  <div className="p-4 border flex items-center justify-between gap-4" style={{ background: `linear-gradient(135deg, ${form.primaryColor}20, transparent)`, borderColor: `${form.primaryColor}30`, borderRadius: activeAccent.radius }}>
                    <div>
                      <div className="text-[8px] font-black uppercase tracking-widest mb-1" style={{ color: form.primaryColor }}>Destaque da Edição</div>
                      <h3 className="text-sm font-black leading-tight" style={{ color: isLight ? '#0f172a' : 'white' }}>Os 10 álbuns que mudaram a percepção sonora nesta década</h3>
                    </div>
                    <button className="px-3 py-1.5 text-[9px] font-black uppercase tracking-wider text-white shrink-0 shadow" style={{ backgroundColor: form.primaryColor, borderRadius: activeAccent.pill }}>
                      Ler →
                    </button>
                  </div>

                  {/* Cards Horizontais */}
                  <div className="space-y-2">
                    {[1, 2].map((i) => (
                      <div key={i} className="p-3 border flex gap-3 items-center" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                        <div className="w-12 h-10 shrink-0 flex items-center justify-center text-xs opacity-40 bg-slate-800" style={{ borderRadius: activeAccent.radius }}>🎵</div>
                        <div className="flex-1 min-w-0">
                          <div className="text-[8px] font-bold uppercase tracking-widest" style={{ color: form.primaryColor }}>Review · Crítica</div>
                          <div className="text-xs font-bold truncate" style={{ color: isLight ? '#1e293b' : '#f8fafc' }}>A revolução do synthwave no áudio imersivo espacial</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── PREVIEW 3: MOSAIC GRID (Tech/Games) ── */}
              {form.layoutStyle === 'mosaic_grid' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between">
                  {/* Tech Navbar (Tabs) */}
                  <div className="flex items-center justify-between border-b pb-2" style={{ borderColor: `${form.primaryColor}30` }}>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: form.primaryColor }} />
                      <span className="font-black text-sm tracking-tight uppercase" style={{ color: isLight ? '#0f172a' : 'white' }}>{form.name || 'Tech Mosaico'}</span>
                    </div>
                    <div className="flex gap-1">
                      <span className="px-2 py-0.5 text-[8px] font-black uppercase text-white" style={{ backgroundColor: form.primaryColor, borderRadius: activeAccent.radius }}>Hardware</span>
                      <span className="px-2 py-0.5 text-[8px] font-black uppercase opacity-60">Games</span>
                      <span className="px-2 py-0.5 text-[8px] font-black uppercase opacity-60">IA</span>
                    </div>
                  </div>

                  {/* Hero Duplo Assimétrico */}
                  <div className="grid grid-cols-3 gap-2.5">
                    <div className="col-span-2 p-4 border flex flex-col justify-end min-h-[140px]" style={{ background: `linear-gradient(to top, #0f172a, ${form.primaryColor}30)`, borderColor: `${form.primaryColor}40`, borderRadius: activeAccent.radius }}>
                      <span className="text-[8px] font-black uppercase tracking-wider text-emerald-400 mb-1">🔥 Top Review</span>
                      <h3 className="text-xs font-black text-white leading-snug">Novo processador quântico atinge marcas inéditas</h3>
                    </div>
                    <div className="col-span-1 p-3 border flex flex-col justify-end bg-slate-900" style={{ borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                      <span className="text-[8px] font-black text-orange-400">⚡ Trending</span>
                      <h4 className="text-[10px] font-bold text-slate-200 leading-tight mt-1">O futuro das GPUs na nuvem</h4>
                    </div>
                  </div>

                  {/* Mosaico Inferior */}
                  <div className="grid grid-cols-2 gap-2.5">
                    {[1, 2].map((i) => (
                      <div key={i} className="p-2.5 border flex items-center justify-between" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                        <div className="text-[10px] font-bold truncate" style={{ color: isLight ? '#1e293b' : 'white' }}>Configurando setups de alta performance</div>
                        <span className="text-[9px] font-mono opacity-50">↗</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── PREVIEW 4: EDITORIAL PROSE (Literatura/Histórias) ── */}
              {form.layoutStyle === 'editorial_prose' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between text-center">
                  {/* Header Literário */}
                  <div className="pb-3 border-b space-y-1" style={{ borderColor: `${form.primaryColor}20` }}>
                    <span className="text-[8px] font-mono uppercase tracking-widest opacity-50">Edição Especial · Volume 42</span>
                    <h2 className="text-xl font-black tracking-tight" style={{ color: isLight ? '#0f172a' : 'white' }}>{form.name || 'Crônicas & Prosa'}</h2>
                    <div className="flex justify-center items-center gap-3 text-[8px] uppercase tracking-[0.2em] opacity-60">
                      <span>Filosofia</span><span>·</span><span>Viagens</span><span>·</span><span>Ensaios</span>
                    </div>
                  </div>

                  {/* Coluna Única Centralizada */}
                  <div className="max-w-md mx-auto p-4 border text-left space-y-2" style={{ backgroundColor: activeTheme.preview.card, borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                    <div className="text-[8px] font-black uppercase tracking-widest" style={{ color: form.primaryColor }}>Ensaio Principal</div>
                    <h3 className="text-sm font-bold leading-snug" style={{ color: isLight ? '#0f172a' : 'white' }}>
                      O silêncio das montanhas: Uma jornada pelas antigas rotas de chá na Ásia Central
                    </h3>
                    <p className="text-[9px] italic leading-relaxed opacity-70">
                      "Caminhar entre os desfiladeiros esquecidos é compreender que o tempo opera em ritmos geológicos..."
                    </p>
                  </div>

                  {/* Lista estilo Jornal */}
                  <div className="max-w-md mx-auto text-left divide-y divide-current/20 text-[10px]">
                    <div className="py-2 flex justify-between items-center">
                      <span className="font-bold truncate" style={{ color: isLight ? '#334155' : '#e2e8f0' }}>A arquitetura minimalista de Kyoto</span>
                      <span className="font-mono text-[8px] opacity-50">8 min ler</span>
                    </div>
                    <div className="py-2 flex justify-between items-center">
                      <span className="font-bold truncate" style={{ color: isLight ? '#334155' : '#e2e8f0' }}>Cartas de um inverno nórdico distante</span>
                      <span className="font-mono text-[8px] opacity-50">12 min ler</span>
                    </div>
                  </div>
                </div>
              )}

              {/* ── PREVIEW 5: DASHBOARD PORTAL (Finanças/Dados) ── */}
              {form.layoutStyle === 'dashboard_portal' && (
                <div className="space-y-3 relative z-10 flex-1 flex flex-col justify-between">
                  {/* Topbar com KPIs */}
                  <div className="flex justify-between items-center p-2 bg-slate-950 border border-slate-800 text-[9px] font-mono" style={{ borderRadius: activeAccent.radius }}>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: form.primaryColor }} />
                      <span className="font-black text-white">{form.name || 'BI Portal'}</span>
                    </div>
                    <div className="flex gap-3">
                      <span>BTC <strong className="text-emerald-400">+4.2%</strong></span>
                      <span>AO VIVO <strong style={{ color: form.primaryColor }}>24/7</strong></span>
                    </div>
                  </div>

                  {/* Sidenav + Main Simulado */}
                  <div className="flex gap-2.5 flex-1">
                    {/* Sidenav fina */}
                    <div className="w-20 p-2 bg-slate-950/80 border border-slate-800/80 space-y-1.5 text-[8px] font-mono text-slate-400" style={{ borderRadius: activeAccent.radius }}>
                      <div className="text-white font-bold p-1 bg-slate-800 rounded">● Mercado</div>
                      <div className="p-1 hover:text-white">○ Cripto</div>
                      <div className="p-1 hover:text-white">○ Ações</div>
                      <div className="p-1 hover:text-white">○ Macro</div>
                    </div>

                    {/* Main Feed */}
                    <div className="flex-1 space-y-2">
                      <div className="p-3 border bg-slate-900/90" style={{ borderColor: `${form.primaryColor}40`, borderRadius: activeAccent.radius }}>
                        <span className="text-[8px] font-mono uppercase px-1.5 py-0.5 bg-emerald-500/20 text-emerald-400 rounded">Breaking</span>
                        <h4 className="text-xs font-bold text-white mt-1">Banco Central anuncia novas diretrizes para ativos digitais</h4>
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div className="p-2 border bg-slate-950/60 text-[9px]" style={{ borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                          <div className="text-slate-400 font-mono">Inflação Global</div>
                          <div className="font-bold text-white mt-0.5">Análise Trimestral →</div>
                        </div>
                        <div className="p-2 border bg-slate-950/60 text-[9px]" style={{ borderColor: activeTheme.preview.border, borderRadius: activeAccent.radius }}>
                          <div className="text-slate-400 font-mono">Tech Stocks</div>
                          <div className="font-bold text-white mt-0.5">Relatório IA →</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* ── PREVIEW 6: VIDEO CINEMA (YouTube / Streaming / Dark Mode) ── */}
              {form.layoutStyle === 'video_cinema' && (
                <div className="space-y-4 relative z-10 flex-1 flex flex-col justify-between text-white bg-slate-950 p-4 rounded-2xl border border-slate-800">
                  <div className="flex justify-between items-center pb-2 border-b border-slate-800">
                    <span className="font-black text-sm uppercase tracking-wider text-red-500">🎬 {form.name || 'Cinema & Streaming'}</span>
                    <span className="text-[9px] font-mono bg-red-600/20 text-red-400 px-2 py-0.5 rounded border border-red-500/30">4K ULTRA HD</span>
                  </div>
                  <div className="relative h-32 rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center border border-slate-800 group cursor-pointer shadow-2xl">
                    <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
                    <div className="w-10 h-10 rounded-full bg-red-600/90 text-white flex items-center justify-center text-lg shadow-[0_0_20px_rgba(220,38,38,0.8)] z-10">▶</div>
                    <div className="absolute bottom-2 left-3 right-3 z-10">
                      <span className="text-[8px] font-bold uppercase tracking-widest text-red-400">🔥 Trailer Oficial</span>
                      <h4 className="text-xs font-black truncate">A Produção Audiovisual por Inteligência Artificial</h4>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {[1, 2].map((i) => (
                      <div key={i} className="p-2 bg-slate-900/80 rounded-lg border border-slate-800 flex items-center gap-2">
                        <div className="w-8 h-8 rounded bg-slate-800 flex items-center justify-center text-xs">🎥</div>
                        <div className="min-w-0 flex-1">
                          <div className="text-[9px] font-bold truncate">Bastidores da Síntese Neural</div>
                          <div className="text-[8px] text-slate-500">10:45 • 15K views</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── PREVIEW 7: MINIMAL ZEN (Apple / Medium / Foco na Leitura) ── */}
              {form.layoutStyle === 'minimal_zen' && (
                <div className="space-y-6 relative z-10 flex-1 flex flex-col justify-between max-w-sm mx-auto w-full py-2">
                  <div className="text-center pb-4 border-b border-current/10 space-y-1">
                    <span className="text-[8px] font-mono tracking-widest uppercase opacity-40">Ensaios & Pensamentos</span>
                    <h2 className="text-lg font-bold tracking-tight" style={{ color: isLight ? '#0f172a' : 'white' }}>{form.name || 'Minimal Zen'}</h2>
                  </div>
                  <div className="space-y-3 text-left">
                    <div className="space-y-1">
                      <span className="text-[8px] font-mono text-emerald-500 font-bold uppercase tracking-widest">Filosofia Digital</span>
                      <h3 className="text-sm font-bold leading-snug" style={{ color: isLight ? '#0f172a' : 'white' }}>A arte do silêncio na era da saturação de informação</h3>
                      <p className="text-[10px] opacity-60 leading-relaxed">Como encontrar clareza mental quando os algoritmos disputam cada segundo da nossa atenção...</p>
                    </div>
                  </div>
                  <div className="pt-3 border-t border-current/10 flex justify-between items-center text-[9px] font-mono opacity-50">
                    <span>Leitura limpa e sem distrações</span>
                    <span>→</span>
                  </div>
                </div>
              )}

              {/* ── PREVIEW 8: CYBER TERMINAL (Hacker / Matrix / Cripto) ── */}
              {form.layoutStyle === 'cyber_terminal' && (
                <div className="space-y-3 relative z-10 flex-1 flex flex-col justify-between bg-black text-emerald-400 p-4 rounded-xl border border-emerald-500/40 font-mono text-[10px] shadow-[0_0_25px_rgba(16,185,129,0.15)]">
                  <div className="flex justify-between items-center pb-2 border-b border-emerald-500/30 text-[9px]">
                    <span className="flex items-center gap-1.5 font-bold">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                      root@colmeia:~# {form.name || 'cyber_feed'}
                    </span>
                    <span className="text-emerald-600">[SYS_OK]</span>
                  </div>
                  <div className="space-y-2 text-left">
                    <div className="p-2 bg-emerald-950/30 border border-emerald-500/20 rounded">
                      <div className="text-emerald-500 text-[8px]">&gt; EXEC_REPORT --latest</div>
                      <div className="text-white font-bold mt-0.5">Novo protocolo cripto atinge consenso em 400ms</div>
                    </div>
                    <div className="p-2 bg-emerald-950/20 border border-emerald-500/10 rounded opacity-80">
                      <div className="text-emerald-600 text-[8px]">&gt; FETCH_LOGS --security</div>
                      <div className="text-slate-300 mt-0.5">Análise de vulnerabilidades zero-day em contratos inteligentes</div>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-emerald-500/30 flex justify-between text-[8px] text-emerald-600">
                    <span>TERMINAL_V2.4 // SECURE</span>
                    <span className="animate-pulse">_</span>
                  </div>
                </div>
              )}

              {/* Footer comum do Simulador */}
              <div className="mt-3 pt-2 border-t flex justify-between items-center text-[9px] opacity-50 font-mono" style={{ borderColor: `${form.primaryColor}20` }}>
                <span>© 2026 {form.name} • Cérebro Autônomo</span>
                <div className="flex items-center gap-1.5">
                  <span>Layout: {form.layoutStyle}</span>
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: form.primaryColor }} />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
