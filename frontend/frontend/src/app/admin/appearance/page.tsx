import React from 'react';
import db from '@/lib/db';
import AppearanceClient from './AppearanceClient';

export const dynamic = 'force-dynamic';

export default async function AppearancePage() {
  const blogsRaw = db.prepare('SELECT * FROM Blog ORDER BY name ASC').all() as any[];

  const blogs = blogsRaw.map((b) => ({
    id: String(b.id),
    name: b.name || 'Portal sem nome',
    domain: b.domain || '',
    niche: b.niche || 'Geral',
    description: b.description || '',
    theme: b.theme || 'dark',
    primaryColor: b.primaryColor || '#06b6d4',
    secondaryColor: b.secondaryColor || '#3b82f6',
    layoutStyle: b.layoutStyle || 'modern',
    bgPrimary: b.bgPrimary || '#020617',
    bgSurface: b.bgSurface || '#1e293b',
    fontHeading: b.fontHeading || 'Inter',
    fontBody: b.fontBody || 'Inter',
    bannerUrl: b.bannerUrl || '',
  }));

  return <AppearanceClient initialBlogs={blogs} />;
}
