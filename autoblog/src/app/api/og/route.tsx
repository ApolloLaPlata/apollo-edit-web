import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    // Valores padrão
    const title = searchParams.has('title')
      ? searchParams.get('title')?.slice(0, 100)
      : 'O Futuro da Inteligência Artificial';
      
    const siteName = searchParams.has('siteName')
      ? searchParams.get('siteName')
      : 'Auto-Blog CMS';

    return new ImageResponse(
      (
        <div
          style={{
            height: '100%',
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            justifyContent: 'center',
            backgroundColor: '#0f172a',
            backgroundImage: 'radial-gradient(circle at 25px 25px, #1e293b 2%, transparent 0%), radial-gradient(circle at 75px 75px, #1e293b 2%, transparent 0%)',
            backgroundSize: '100px 100px',
            padding: '80px',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '30px',
            }}
          >
            <div
              style={{
                width: '60px',
                height: '60px',
                backgroundColor: '#06b6d4',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '30px',
                fontWeight: 'bold',
                borderRadius: '12px',
                marginRight: '20px',
              }}
            >
              {siteName?.charAt(0) || 'B'}
            </div>
            <span style={{ fontSize: '32px', color: '#cbd5e1', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '4px' }}>
              {siteName}
            </span>
          </div>

          <div
            style={{
              fontSize: '70px',
              fontWeight: 900,
              color: '#ffffff',
              lineHeight: 1.1,
              letterSpacing: '-2px',
              display: '-webkit-box',
              WebkitBoxOrient: 'vertical',
              WebkitLineClamp: 3,
              overflow: 'hidden',
              textShadow: '0 4px 20px rgba(0,0,0,0.5)',
            }}
          >
            {title}
          </div>

          <div
            style={{
              display: 'flex',
              marginTop: '40px',
              alignItems: 'center',
            }}
          >
            <div style={{ color: '#38bdf8', fontSize: '24px', fontWeight: 'bold' }}>
              Leia a matéria completa na plataforma
            </div>
          </div>
        </div>
      ),
      {
        width: 1200,
        height: 630,
      }
    );
  } catch (e: any) {
    console.error(e);
    return new Response(`Failed to generate image`, {
      status: 500,
    });
  }
}
