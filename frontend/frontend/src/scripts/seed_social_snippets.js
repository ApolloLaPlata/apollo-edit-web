const db = require('./node_modules/better-sqlite3')('./dev.db');
const crypto = require('crypto');

console.log('Semeando Iscas Sociais Omni-Channel para os 4 artigos interativos...');

const posts = db.prepare("SELECT id, title, slug, blogId, postType FROM Post WHERE postType IN ('audio_track', 'video_series', 'photo_gallery', 'news_timeline')").all();

if (posts.length === 0) {
  console.log('Nenhum post interativo encontrado no banco. Execute seed_interactive_posts.js primeiro.');
  process.exit(0);
}

const snippets = [
  {
    platform: 'instagram',
    postType: 'audio_track',
    content: `📸🚨 A TRILHA SONORA OFICIAL DAS MADRUGADAS DE CÓDIGO! 🎧⚡\n\nVocê já sentiu que o silêncio absoluto ou músicas comuns quebram o seu estado de flow no terminal?\n\nO Phonk e o Dark Trap deixaram de ser apenas subgêneros de nicho para se tornarem a batida oficial dos engenheiros de IA e pilotos de alta velocidade! 🔥\n\n👉 Preparamos um PLAYER DE ÁUDIO INTERATIVO com uma playlist neural exclusiva direto em nosso portal!\n\n🔗 Clique no link da bio para ouvir agora enquanto coda! #DarkTrap #Phonk #CyberCulture #DevLife #AI`
  },
  {
    platform: 'twitter',
    postType: 'video_series',
    content: `🧵 1/4 Por que 90% dos portais de notícias falham ao tentar escalar com Inteligência Artificial? 🤖⚡\n\nA resposta não está no modelo de linguagem, mas sim no PROTOCOLO DE AUTOMAÇÃO EDITORIAL.\n\nLançamos hoje uma Minissérie em Vídeo em 4 Episódios sobre Agentes Neurais e Automação no CMS! 👇\n\n🧵 2/4 No Episódio 1, mostramos como os transformers mudaram a sintaxe e a busca por palavras-chave cauda longa no Google Core Web Vitals sem esforço manual.\n\n🧵 3/4 Já no Episódio 2 e 3, abrimos a caixa preta do Protocolo Colmeia e como sincronizar 20 portais com design e temas únicos!\n\n🔗 Assista aos 4 capítulos completos no seletor de episódios do nosso portal! 🎬🚀`
  },
  {
    platform: 'linkedin',
    postType: 'photo_gallery',
    content: `💼 ARQUITETURA DE SISTEMAS & IDENTIDADE VISUAL EM ESCALA ENTERPRISE\n\nComo manter uma frota de veículos de mídia digital operando com alta performance editorial e, ao mesmo tempo, garantir que cada portal possua uma identidade visual única, sem parecer um clone genérico?\n\nEm nossa mais recente cobertura de bastidores, documentamos a arquitetura visual do Estúdio Antigravity. Não se trata apenas de paletas de cores, mas de tipografia editorial de precisão (Google Fonts) e componentes interativos nativos sem diálogos intrusivos.\n\n📸 Disponibilizamos um ensaio técnico completo em nossa Galeria Mosaico Interativa com modo Lightbox em alta resolução.\n\n🔗 Confira o estudo de caso completo em nosso portal e compartilhe suas impressões sobre o design de interfaces autônomas.`
  },
  {
    platform: 'telegram',
    postType: 'news_timeline',
    content: `✈️🚨 ALERTA VIP • BREAKING NEWS • DIRETRIZ GLOBAL DE IA ⚡\n\n⚠️ O Banco Central e os órgãos de regulamentação emitiram comunicados urgentes sobre protocolos descentralizados e inteligência autônoma.\n\nO que você precisa saber em 3 pontos:\n• 📉 Mercado asiático e europeu reagem com forte volatilidade no setor de processamento neural.\n• 🛡️ Frota Antigravity confirma sincronização total da colmeia sem perda de contexto.\n• ⚡ Módulos Interativos de IA são implementados para cobertura cronológica em tempo real.\n\n⏱️ Mapeamos toda a evolução dos acontecimentos minuto a minuto em nossa LINHA DO TEMPO INTERATIVA.\n\n🔗 Acesse agora o link abaixo e veja o desdobramento cronológico completo!`
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
    console.log(`✓ Isca [${s.platform.toUpperCase()}] criada para post: "${targetPost.title.substring(0, 35)}..."`);
  }
}

db.close();
console.log(`\nSucesso! ${count} iscas sociais omni-channel foram adicionadas à central!`);
