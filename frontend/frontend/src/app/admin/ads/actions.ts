'use server';

import db from '@/lib/db';
import { revalidatePath } from 'next/cache';

export async function saveAdConfig(formData: FormData) {
  const blogId = formData.get('blogId') as string;
  const horizontalCode = formData.get('horizontalCode') as string;
  const squareCode = formData.get('squareCode') as string;
  const verticalCode = formData.get('verticalCode') as string;

  if (!blogId) return;

  const insertStmt = db.prepare(`
    INSERT INTO Ads (id, blogId, type, code) 
    VALUES (?, ?, ?, ?)
    ON CONFLICT(blogId, type) 
    DO UPDATE SET code = excluded.code
  `);

  try {
    if (horizontalCode !== undefined) {
      insertStmt.run(crypto.randomUUID(), blogId, 'horizontal', horizontalCode);
    }
    if (squareCode !== undefined) {
      insertStmt.run(crypto.randomUUID(), blogId, 'square', squareCode);
    }
    if (verticalCode !== undefined) {
      insertStmt.run(crypto.randomUUID(), blogId, 'vertical', verticalCode);
    }
    
    revalidatePath('/admin/ads');
    revalidatePath('/', 'layout'); // Invalidate public caches to show new ads
  } catch (error) {
    console.error("Erro ao salvar Ads:", error);
  }
}
