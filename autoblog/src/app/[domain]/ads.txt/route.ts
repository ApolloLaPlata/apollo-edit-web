import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request, props: { params: Promise<{ domain: string }> }) {
  const params = await props.params;
  const decodedDomain = decodeURIComponent(params.domain);

  // Idealmente, existe uma coluna `adsTxt` na tabela Blog.
  // Caso a tabela não a possua, usamos um padrão estático baseado no Publisher ID principal (hardcoded provisoriamente)
  let adsTxtContent = "";

  try {
     const blog = db.prepare('SELECT id FROM Blog WHERE domain = ?').get(decodedDomain) as any;
     if (!blog) {
       return new NextResponse('Blog não encontrado', { status: 404 });
     }
     
     // Placeholder: Configuração padrão do Google AdSense
     // No futuro, isso pode ser puxado do banco: `SELECT adsTxt FROM Blog WHERE id = ?`
     adsTxtContent = `google.com, pub-0000000000000000, DIRECT, f08c47fec0942fa0
outbrain.com, 000000, DIRECT
taboola.com, 000000, DIRECT`;

  } catch(e) {
     console.error('Erro gerando Ads.txt', e);
  }

  return new NextResponse(adsTxtContent, {
    headers: {
      'Content-Type': 'text/plain',
      'Cache-Control': 's-maxage=86400, stale-while-revalidate',
    },
  });
}
