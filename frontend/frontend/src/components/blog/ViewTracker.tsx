'use client';

import { useEffect } from 'react';

export default function ViewTracker({ postId }: { postId: string }) {
  useEffect(() => {
    // Registra a view (fire and forget)
    fetch('/api/analytics/view', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ postId })
    }).catch(() => {});
  }, [postId]);

  return null; // Não renderiza nada visual
}
