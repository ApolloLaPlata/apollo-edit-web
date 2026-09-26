import { NextResponse } from 'next/server';
import db from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const blogId = searchParams.get('blogId') || 'global';

    let niche = 'Tecnologia & Inteligência Artificial';
    if (blogId !== 'global') {
      const blog = db.prepare('SELECT name, niche, personaPrompt FROM Blog WHERE id = ?').get(blogId) as any;
      if (blog && blog.niche) niche = blog.niche;
      else if (blog && blog.name) niche = blog.name;
    }

    // Gerar radar de palavras-chave cauda longa (Long-Tail Keywords) de alta conversão
    const keywords = [
      {
        id: 'kw-1',
        keyword: `como ganhar dinheiro com ${niche.toLowerCase()} em 2026`,
        volume: '18.400 / mês',
        kd: 'Baixa 🟢',
        cpc: 'R$ 4,50',
        intent: 'Comercial 🔥',
        suggestedTitle: `Guia Completo: Como Monetizar e Lucrar com ${niche} em 2026 sem Investir Nada`
      },
      {
        id: 'kw-2',
        keyword: `melhores ferramentas de ${niche.toLowerCase()} gratuitas`,
        volume: '32.100 / mês',
        kd: 'Média 🟡',
        cpc: 'R$ 6,80',
        intent: 'Informativa / Afiliado 🔗',
        suggestedTitle: `As 10 Melhores Ferramentas de ${niche} que São 100% Gratuitas (Lista Atualizada)`
      },
      {
        id: 'kw-3',
        keyword: `tutorial passo a passo ${niche.toLowerCase()} para iniciantes`,
        volume: '45.000 / mês',
        kd: 'Baixa 🟢',
        cpc: 'R$ 3,20',
        intent: 'Educacional 📚',
        suggestedTitle: `Tutorial Definitivo de ${niche} para Iniciantes: Do Zero ao Avançado em 15 Minutos`
      },
      {
        id: 'kw-4',
        keyword: `${niche.toLowerCase()} vale a pena ou é golpe análise`,
        volume: '12.800 / mês',
        kd: 'Baixa 🟢',
        cpc: 'R$ 8,90',
        intent: 'Investigativa / Alta Conversão 🎯',
        suggestedTitle: `Análise Sincera: ${niche} Vale a Pena Mesmo em 2026? Veja os Prós e Contras`
      },
      {
        id: 'kw-5',
        keyword: `tendências e futuro do ${niche.toLowerCase()} no brasil`,
        volume: '9.500 / mês',
        kd: 'Média 🟡',
        cpc: 'R$ 5,10',
        intent: 'Noticiário / Viral ⚡',
        suggestedTitle: `O Futuro do ${niche} no Brasil: O que Especialistas e IAs Preveem para os Próximos Meses`
      }
    ];

    return NextResponse.json({ success: true, niche, keywords });
  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
