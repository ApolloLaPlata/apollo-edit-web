'use server';

import db from '@/lib/db';
import { revalidatePath } from 'next/cache';

export async function toggleAgentConfig(blogId: string, isActive: boolean) {
  try {
    await db.prepare('UPDATE AgentConfig SET isActive = ? WHERE blogId = ?').run(isActive ? 1 : 0, blogId);
    revalidatePath('/admin/plugins');
    return { success: true };
  } catch (error: any) {
    return { error: error.message };
  }
}
