import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request, props: { params: Promise<{ slug: string }> }) {
  const params = await props.params;
  const slug = params.slug;

  const decodedSlug = slug.toLowerCase().replace(/-/g, ' '); // ex: 'curso-de-ia' -> 'curso de ia'

  let targetUrl = 'https://google.com'; // Fallback global de segurança

  try {
    // Busca o Link de Afiliado dinamicamente
    // Compara o keyword do banco (ignorando case) com o slug tratado.
    const affiliate = db.prepare(`SELECT * FROM AffiliateLink WHERE LOWER(keyword) = ? OR LOWER(REPLACE(keyword, ' ', '-')) = ?`).get(decodedSlug, slug.toLowerCase()) as any;

    if (affiliate && affiliate.url) {
      targetUrl = affiliate.url;

      // Fase 66: Tracking Invisível de Cliques
      // Incrementar métrica para sabermos exatamente qual link converte mais
      db.prepare('UPDATE AffiliateLink SET totalClicks = COALESCE(totalClicks, 0) + 1 WHERE id = ?').run(affiliate.id);
    }
  } catch (error) {
    console.error(`[CLOAKING ERROR] Falha ao processar /go/${slug}:`, error);
  }

  // Registra no Log do Servidor que houve um clique de Cloaking
  console.log(`[CLOAKING ENGAGED] Redirecionando clique /go/${slug} -> ${targetUrl.substring(0, 30)}...`);

  // Redirecionamento 307 (Temporary Redirect) 
  // Usa 307 ao invés de 301 para que o Google não faça cache do link, mantendo o controle no nosso lado.
  return NextResponse.redirect(targetUrl, {
    status: 307,
    headers: {
      'Cache-Control': 'no-store, max-age=0',
      'X-Robots-Tag': 'noindex, nofollow' // Blindagem contra o Googlebot
    }
  });
}
