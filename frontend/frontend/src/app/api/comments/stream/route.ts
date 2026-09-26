export const runtime = 'edge';

/**
 * 📡 ASTROTURFING BRIDGE (D1 SSE Stream - Etapa 6)
 * Server-Sent Events (SSE) rodando no Edge (Cloudflare Worker).
 * Ele envia comentários novos para a tela do usuário em tempo real
 * sem precisar recarregar a página (Efeito Twitch TV).
 */
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const postId = searchParams.get('postId');

  if (!postId) return new Response("Missing postId", { status: 400 });

  console.log(`[SSE] 🔌 Nova conexão Real-Time estabelecida no Post ${postId}...`);

  const encoder = new TextEncoder();
  let intervalId: any;

  const customReadable = new ReadableStream({
    start(controller) {
      // 1. Envia a conexão inicial
      controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'CONNECTED' })}\n\n`));

      // 2. Simula o banco de dados disparando mensagens em Tempo Real (Astroturfing Bot)
      // Em produção real, leríamos o Cloudflare D1 a cada X segundos ou usaríamos DO (Durable Objects) / Pusher.
      intervalId = setInterval(() => {
        // Envia um ping pra manter a conexão viva (Cloudflare timeout bypass)
        controller.enqueue(encoder.encode(`: ping\n\n`));
      }, 15000);
    },
    cancel() {
      if (intervalId) clearInterval(intervalId);
      console.log(`[SSE] 🚫 Usuário fechou a aba. Desconectado do Post ${postId}.`);
    }
  });

  return new Response(customReadable, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
    }
  });
}
