import { NextResponse } from 'next/server';

/**
 * ☠️ API DA RATOEIRA (Zero-Trust Security)
 * Se qualquer IP pingar nessa rota, significa que ele é um Bot que ignorou
 * as regras de invisibilidade CSS e clicou no link oculto do rodapé.
 * Ele será marcado e banido.
 */
export async function GET(request: Request) {
  // Pega o IP do Bot
  const ip = request.headers.get('x-forwarded-for') || 'IP-Desconhecido';
  const userAgent = request.headers.get('user-agent') || 'Bot-Desconhecido';

  console.log(`[HONEY-POT] 🚨 RATINHO PEGO NA ARMADILHA!`);
  console.log(`[HONEY-POT] 🩸 IP: ${ip} | User-Agent: ${userAgent}`);
  
  // Em produção, nós salvaríamos esse IP numa tabela `BanList` do SQLite
  // E o middleware.ts rejeitaria ele antes de carregar o site.
  
  // Retorna um erro confuso para atrasar o script de quem está nos hackeando
  return new NextResponse('Fatal Error 0x892934: Infinite Recursive Loop Detected.', { 
    status: 508, // Loop Detected
    headers: {
      'Retry-After': '86400' // Manda o bot tentar de novo só daqui 1 dia
    }
  });
}
