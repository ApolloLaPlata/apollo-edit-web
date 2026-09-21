// ────────────────────────────────────────────────────────────
// LayoutRouter.tsx — Interface compartilhada + roteador central
// Todos os 5 templates recebem exatamente os mesmos dados.
// ────────────────────────────────────────────────────────────
import React from 'react';
import ClassicPortalTemplate from './ClassicPortalTemplate';
import MagazineHeroTemplate from './MagazineHeroTemplate';
import StreamFeedTemplate from './StreamFeedTemplate';
import MosaicGridTemplate from './MosaicGridTemplate';
import EditorialProseTemplate from './EditorialProseTemplate';
import DashboardPortalTemplate from './DashboardPortalTemplate';
import VideoCinemaTemplate from './VideoCinemaTemplate';
import MinimalZenTemplate from './MinimalZenTemplate';
import CyberTerminalTemplate from './CyberTerminalTemplate';
import ConciergeWidget from '../ConciergeWidget';
import MobileBottomNav from '@/components/ui/MobileBottomNav';

export interface PostData {
  id: string | number;
  title: string;
  slug: string;
  contentMd: string;
  coverImage?: string;
  author: string;
  createdAt: string;
  category?: string;
  blog?: { name: string; domain: string };
}

export interface CategoryData {
  name: string;
  slug: string;
}

export interface BlogData {
  id: string | number;
  name: string;
  domain: string;
  niche: string;
  description?: string;
  theme?: string;
  primaryColor?: string;
  secondaryColor?: string;
  layoutStyle?: string;
  fontFamily?: string;
  logoUrl?: string;
  accentStyle?: string;
}

export interface TemplateProps {
  blog: BlogData;
  heroPost: PostData | null;
  otherPosts: PostData[];
  webStories?: any[];
  categories: CategoryData[];
  lang: string;
  domain: string;
}

// Utilitário compartilhado — limpar markdown bruto em excerto limpo
export function cleanExcerpt(markdown: string, maxLen = 180): string {
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

// Formatar data em pt-BR
export function fmtDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' });
  } catch {
    return iso;
  }
}

// Roteador principal — escolhe o template com base em layoutStyle
export default function LayoutRouter(props: TemplateProps) {
  const layout = props.blog.layoutStyle || 'classic_portal';

  const renderTemplate = () => {
    switch (layout) {
      case 'stream_feed':
        return <StreamFeedTemplate {...props} />;
      case 'mosaic_grid':
        return <MosaicGridTemplate {...props} />;
      case 'editorial_prose':
        return <EditorialProseTemplate {...props} />;
      case 'dashboard_portal':
        return <DashboardPortalTemplate {...props} />;
      case 'video_cinema':
        return <VideoCinemaTemplate {...props} />;
      case 'minimal_zen':
        return <MinimalZenTemplate {...props} />;
      case 'cyber_terminal':
        return <CyberTerminalTemplate {...props} />;
      case 'magazine_hero':
        return <MagazineHeroTemplate {...props} />;
      case 'classic_portal':
      default:
        return <ClassicPortalTemplate {...props} />;
    }
  };

  return (
    <div className="md:pb-0 pb-20 relative">
      {renderTemplate()}
      
      {/* GLOBAL WIDGETS */}
      <ConciergeWidget
        blogId={props.blog.id?.toString() || 'dark-trap'}
        blogName={props.blog.name || 'Portal Executivo'}
        accentColor={props.blog.primaryColor || '#10b981'}
      />
      
      {/* MOBILE APP-LIKE NAVBAR */}
      <MobileBottomNav lang={props.lang} domain={props.domain} />
    </div>
  );
}

