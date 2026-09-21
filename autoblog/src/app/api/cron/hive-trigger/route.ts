import { NextResponse } from 'next/server';
import { executeAutonomousEditorialCycle } from '@/lib/agents/autonomous_engine';

/**
 * 🐝 COLMEIA: HEARTBEAT (Gatilho Autônomo)
 * GET /api/cron/hive-trigger
 * 
 * Esta rota deve ser chamada periodicamente (ex: a cada 30 min por um serviço de Cron como Vercel/Cron-job.org).
 * Ela desperta o motor neural que:
 * 1. Puxa tendências (ou resgata vídeos do YouTube vinculados).
 * 2. Toma a decisão editorial com o O3.
 * 3. Escreve a matéria com Claude Sonnet.
 * 4. Faz SEO e formata com GPT-5.
 * 5. Salva no banco de dados e adiciona à fila de renderização de vídeo (Cross-Channel).
 */
export async function GET(request: Request) {
  try {
    const authHeader = request.headers.get('authorization');
    // Em produção, isso seria verificado contra um CRON_SECRET nas env vars
    // if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    //   return NextResponse.json({ error: 'Não autorizado' }, { status: 401 });
    // }

    console.log("🐝 [HIVE TRIGGER] Despertando a Colmeia para o ciclo de auto-gestão editorial...");
    
    // O motor varre todos os blogs cadastrados e posta neles com base no contexto (limite de 3 dia, etc).
    const result = await executeAutonomousEditorialCycle();

    return NextResponse.json({ 
      status: 'success', 
      message: 'Ciclo neural completado.', 
      data: result 
    }, { status: 200 });

  } catch (error: any) {
    console.error("🐝 [HIVE TRIGGER] Erro fatal:", error);
    return NextResponse.json({ status: 'error', message: error.message }, { status: 500 });
  }
}
