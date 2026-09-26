const db = require('./node_modules/better-sqlite3')('./dev.db');
const crypto = require('crypto');

console.log('Semeando Iscas das 8 Redes Sociais + Newsletter do usuário...');

const posts = await db.prepare("SELECT id, title, slug, blogId, postType FROM Post WHERE postType IN ('audio_track', 'video_series', 'photo_gallery', 'news_timeline')").all();

if (posts.length === 0) {
  console.log('Nenhum post encontrado.');
  process.exit(0);
}

const snippets = [
  {
    platform: 'youtube',
    postType: 'video_series',
    content: `📺 ROTEIRO YOUTUBE SHORTS / LONGO\n\n[HOOK VISUAL 0s-3s]: "Você ainda está rodando agentes de IA no modo manual? Pare agora!"\n\n[STORY 3s-25s]: "Nesta série em 4 episódios, nós abrimos a caixa preta do Protocolo Colmeia e mostramos como sincronizar múltiplos portais sem perda de contexto e com design único para cada veículo."\n\n[CTA 25s-30s]: "Assista aos episódios completos no link fixado no primeiro comentário! Se inscreva para não perder os próximos drops!"\n\n🏷️ TAGS: #InteligenciaArtificial #Automação #WebDev #Nextjs #AI #Tech`
  },
  {
    platform: 'facebook',
    postType: 'news_timeline',
    content: `👥 PERGUNTA PARA A COMUNIDADE:\n\nComo a regulamentação global e as novas diretrizes do Banco Central para Inteligência Autônoma estão impactando os seus projetos digitais neste momento?\n\nMontamos uma LINHA DO TEMPO CRONOLÓGICA completa mapeando todos os acontecimentos minuto a minuto em nosso portal.\n\n👇 Deixe sua opinião aqui nos comentários e acesse a cobertura interativa completa no link abaixo!`
  },
  {
    platform: 'tiktok',
    postType: 'audio_track',
    content: `🎵 ROTEIRO TIKTOK (30s VIRAL)\n\n[TEXTO NA TELA]: A Trilha Sonora Secreta dos Programadores 🎧🔥\n[ÁUDIO DE FUNDO]: Batida Phonk / Dark Trap em alta.\n\n[LOCUÇÃO FAZENDO CORTES RÁPIDOS]: "Descobrimos por que o Phonk e o Dark Trap viraram o combustível de alta velocidade dos desenvolvedores neurais!\nEsqueça playlists comuns: criamos um player de áudio interativo direto na matéria com faixas neurais exclusivas para codar em flow absoluto."\n\n👉 Clica no link do perfil para ouvir agora enquanto coda! #DarkTrap #Phonk #DevTok #CodeLife #AI`
  },
  {
    platform: 'kwai',
    postType: 'photo_gallery',
    content: `⚡ ALERTA KWAI • BASTIDORES EXCLUSIVOS!\n\nVocê sabe como manter dezenas de sites operando com alta tecnologia sem que eles pareçam clones genéricos?\n\nVem ver os bastidores do Estúdio Visual Antigravity! Montamos uma galeria de fotos interativa em alta resolução mostrando cada detalhe da nossa arquitetura.\n\n🔥 Clica logo no link e confira essa aula de design e automação! #Kwai #Tecnologia #Design #Inovacao #Bastidores`
  },
  {
    platform: 'dailymotion',
    postType: 'video_series',
    content: `🎬 DESCRIÇÃO CANAL DAILYMOTION (HD)\n\nTítulo: A Evolução dos Agentes Neurais no CMS - Série Completa (4 Episódios)\n\nResumo Técnico:\nNeste documentário técnico, exploramos como os modelos transformers e pipelines assíncronos mudaram a automação de conteúdo editorial. A série é dividida em 4 capítulos práticos, cobrindo desde a sintaxe SEO até a sincronização de memória em tempo real.\n\n⏱️ TIMESTAMPS:\n00:00 - Introdução: O Fim do Trabalho Manual\n03:15 - Cap 1: Como funcionam os Agentes Neurais\n08:40 - Cap 2: Sincronização Colmeia e Memória Ativa\n14:20 - Cap 3: Módulos Interativos e Multimídia\n21:00 - Conclusão: Escalabilidade Enterprise\n\n🔗 Inscreva-se em nosso canal Dailymotion e acompanhe o portal!`
  },
  {
    platform: 'newsletter',
    postType: 'news_timeline',
    content: `✉️ DAILY DROP • PÍLULA DE NOTÍCIAS (NEWSLETTER)\n\nOlá, leitor VIP!\n\nAqui está o seu resumo em 3 pontos sobre as movimentações mais importantes de hoje:\n\n• 🌐 **Regulamentação Global**: Emitidas novas diretrizes sobre inteligência autônoma em portais de notícias.\n• ⚡ **Frota Antigravity**: Confirmada sincronização em tempo real com módulos interativos (Áudio, Vídeo e Timeline).\n• 📈 **Impacto de Mercado**: Setor responde com alta demanda por automação descentralizada.\n\n🔗 [CLIQUE AQUI] para ler a análise completa na nossa Linha do Tempo Interativa e ver os gráficos interativos no portal!`
  }
];

const insertStmt = db.prepare(`
  INSERT INTO SocialSnippet (id, postId, platform, content)
  VALUES (?, ?, ?, ?)
`);

let count = 0;
for (const s of snippets) {
  const targetPost = posts.find(p => p.postType === s.postType) || posts[0];
  if (targetPost) {
    insertStmt.run(crypto.randomUUID(), targetPost.id, s.platform, s.content);
    count++;
    console.log(`✓ Isca [${s.platform.toUpperCase()}] adicionada para post: "${targetPost.title.substring(0, 30)}..."`);
  }
}

db.close();
console.log(`\nSucesso! ${count} roteiros das novas plataformas foram injetados na central!`);
