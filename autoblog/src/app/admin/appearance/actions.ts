'use server';

import db from '@/lib/db';
import { revalidatePath } from 'next/cache';

export async function saveAppearance(formData: FormData) {
  const blogId      = formData.get('blogId') as string;
  const name        = formData.get('name') as string;
  const theme       = formData.get('theme') as string;
  const description = formData.get('description') as string;
  const primaryColor   = (formData.get('primaryColor') as string)   || '#06b6d4';
  const secondaryColor = (formData.get('secondaryColor') as string)  || '#3b82f6';
  const bgPrimary      = (formData.get('bgPrimary') as string)       || '#020617';
  const bgSurface      = (formData.get('bgSurface') as string)       || '#1e293b';
  const fontHeading    = (formData.get('fontHeading') as string)     || 'Inter';
  const fontBody       = (formData.get('fontBody') as string)        || 'Inter';
  const bannerUrl      = (formData.get('bannerUrl') as string)       || '';
  const layoutStyle    = (formData.get('layoutStyle') as string)     || 'classic_portal';
  const fontFamily     = (formData.get('fontFamily') as string)      || 'inter';
  const logoUrl        = (formData.get('logoUrl') as string)         || '';
  const accentStyle    = (formData.get('accentStyle') as string)     || 'rounded';
  const activeFeatures = (formData.get('activeFeatures') as string)  || '["article","video_series","audio_track","photo_gallery","news_timeline"]';
  const socialLinks    = (formData.get('socialLinks') as string)     || '{}';

  if (!blogId || !name || !theme) {
    return { error: 'Blog, Nome e Tema são obrigatórios' };
  }

  try {
    await db.prepare(`
      UPDATE Blog 
      SET name = ?, theme = ?, description = ?, primaryColor = ?, secondaryColor = ?,
          bgPrimary = ?, bgSurface = ?, fontHeading = ?, fontBody = ?, bannerUrl = ?,
          layoutStyle = ?, fontFamily = ?, logoUrl = ?, accentStyle = ?, activeFeatures = ?, socialLinks = ?, updatedAt = ?
      WHERE id = ?
    `).run(
      name, theme, description, primaryColor, secondaryColor,
      bgPrimary, bgSurface, fontHeading, fontBody, bannerUrl,
      layoutStyle, fontFamily, logoUrl, accentStyle, activeFeatures, socialLinks,
      new Date().toISOString(),
      blogId
    );
    revalidatePath('/', 'layout');
    revalidatePath('/admin/appearance');
    return { success: true };
  } catch (error: any) {
    return { error: error.message };
  }
}
