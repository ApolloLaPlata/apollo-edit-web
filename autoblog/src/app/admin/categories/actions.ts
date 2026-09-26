'use server';

import db from '@/lib/db';
import { revalidatePath } from 'next/cache';
import crypto from 'crypto';

export async function addCategory(formData: FormData) {
  const name = formData.get('name') as string;
  const blogId = formData.get('blogId') as string;

  if (!name || !blogId) {
    return { error: 'Nome e Blog ID são obrigatórios' };
  }

  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
  const id = crypto.randomUUID();

  try {
    await db.prepare('INSERT INTO Category (id, name, slug, blogId) VALUES (?, ?, ?, ?)').run(id, name, slug, blogId);
    revalidatePath('/admin/categories');
    return { success: true };
  } catch (error: any) {
    return { error: error.message };
  }
}

export async function deleteCategory(id: string) {
  try {
    await db.prepare('DELETE FROM Category WHERE id = ?').run(id);
    revalidatePath('/admin/categories');
    return { success: true };
  } catch (error: any) {
    return { error: error.message };
  }
}
