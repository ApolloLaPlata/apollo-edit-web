import { NextResponse } from 'next/server';
import db from '@/lib/db';

// PNG Transparente 1x1 base64
const TRANSPARENT_PIXEL_BASE64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=';
const pixelBuffer = Buffer.from(TRANSPARENT_PIXEL_BASE64, 'base64');

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const email = searchParams.get('email');
    const blogId = searchParams.get('blogId');

    if (email) {
      // Atualiza a taxa de abertura
      // Isso indica que o usuário abriu o e-mail no cliente dele
      if (blogId) {
        db.prepare('UPDATE Subscriber SET opens = opens + 1 WHERE email = ? AND blogId = ?').run(email, blogId);
      } else {
        db.prepare('UPDATE Subscriber SET opens = opens + 1 WHERE email = ?').run(email);
      }
      console.log(`[NEWSLETTER-TRACKER] 👁️ Abertura registrada para o lead: ${email}`);
    }

    // Retorna a imagem transparente com cache desativado
    return new NextResponse(pixelBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'image/png',
        'Content-Length': pixelBuffer.length.toString(),
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0',
      },
    });
  } catch (error) {
    console.error('[NEWSLETTER-TRACKER] Erro no pixel:', error);
    // Mesmo em erro, devolve o pixel para não quebrar o layout do email do cliente
    return new NextResponse(pixelBuffer, {
      status: 200,
      headers: { 'Content-Type': 'image/png' },
    });
  }
}
