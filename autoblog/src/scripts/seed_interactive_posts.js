const db = require('./node_modules/better-sqlite3')('./dev.db');

const blogs = db.prepare('SELECT id, domain, name FROM Blog').all();
if (blogs.length === 0) {
  console.log('Nenhum blog encontrado.');
  process.exit(0);
}

const blog = blogs[0]; // Portal principal
console.log(`Inserindo posts interativos para o blog: ${blog.name} (${blog.domain})`);

// Pegar categoria ou criar uma
let category = db.prepare('SELECT id FROM Category WHERE blogId = ? LIMIT 1').get(blog.id);
if (!category) {
  const catId = 'cat-interact-' + Date.now();
  db.prepare('INSERT INTO Category (id, name, slug, blogId) VALUES (?, ?, ?, ?)').run(catId, 'Mídia & Interatividade', 'midia-interativa', blog.id);
  category = { id: catId };
}

const now = new Date().toISOString();

const posts = [
  {
    id: 'post-audio-' + Date.now(),
    title: '🎧 Dark Trap & Phonk: A Trilha Sonora da Ciber-Cultura (Com Player Interativo)',
    slug: 'dark-trap-phonk-trilha-sonora-ciber-cultura',
    contentMd: `A ascensão da estética cyberpunk e dos sistemas de inteligência artificial autônoma trouxe consigo um novo renascimento musical. O Phonk e o Dark Trap deixaram de ser apenas subgêneros de nicho para se tornarem a batida oficial das madrugadas de programação e pilotagem de alta velocidade.

Utilize o player de áudio acima para explorar a nossa playlist curada diretamente pela Redação Neural do Dark Trap Radio. As frequências de graves profundos e sintetizadores oitavados aumentam o foco cognitivo em ambientes de alta densidade de dados.`,
    coverImage: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1200&q=80',
    postType: 'audio_track',
    mediaPayload: JSON.stringify({
      playlist: [
        {
          title: 'Cyber Drift 2026 (Beat Exclusivo)',
          artist: 'Redação Neural • Dark Trap Radio',
          duration: '3:45',
          genre: 'Phonk / Dark Trap',
          url: 'https://cdn.pixabay.com/download/audio/2022/05/16/audio_db6591201e.mp3?filename=cyberpunk-city-110296.mp3'
        },
        {
          title: 'Neon Highway • 24/7 Mix',
          artist: 'Redação Neural • Beats Autônomos',
          duration: '4:12',
          genre: 'Synthwave / Bass',
          url: 'https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3?filename=synthwave-80s-110045.mp3'
        }
      ]
    })
  },
  {
    id: 'post-video-' + Date.now(),
    title: '🎬 Série Especial em 4 Episódios: A Evolução dos Agentes Neurais e Automação',
    slug: 'serie-especial-4-episodios-evolucao-agentes-neurais',
    contentMd: `Entender como um ecossistema autônomo opera em escala exige mais do que um simples texto descritivo. Por isso, preparamos uma minissérie em vídeo em 4 capítulos para você assistir na íntegra em nossa plataforma.

Navegue pelo seletor de episódios no player acima. Abordamos desde o funcionamento interno dos modelos de linguagem em nuvem até a estratégia prática de SEO cauda longa que garante liderança nas métricas do Google Core Web Vitals.`,
    coverImage: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80',
    postType: 'video_series',
    mediaPayload: JSON.stringify({
      seriesTitle: 'Minissérie: Automação Editorial Exponencial (4 Capítulos)',
      episodes: [
        {
          title: 'Episódio 1: O Despertar dos Modelos Neurais',
          duration: '12:40',
          youtubeId: 'dQw4w9WgXcQ',
          summary: 'Como os primeiros transformers mudaram o paradigma da sintaxe de código e jornalismo.'
        },
        {
          title: 'Episódio 2: A Arquitetura de Agentes Autônomos',
          duration: '15:20',
          youtubeId: 'jNQXAC9IVRw',
          summary: 'Os bastidores do protocolo Colmeia e a sincronização em tempo real.'
        },
        {
          title: 'Episódio 3: SEO Cauda Longa e Scraping Contínuo',
          duration: '09:15',
          youtubeId: 'L_LUpnjgPso',
          summary: 'A estratégia que garante pontuação 90+ no Core Web Vitals sem esforço manual.'
        },
        {
          title: 'Episódio 4: Designizações, Temas e Identidade Visual',
          duration: '14:50',
          youtubeId: 'dQw4w9WgXcQ',
          summary: 'Como manter 20 portais únicos com um único motor de backend.'
        }
      ]
    })
  },
  {
    id: 'post-gallery-' + Date.now(),
    title: '📸 Bastidores em Foco: A Arquitetura Visual do Estúdio Antigravity',
    slug: 'bastidores-foco-arquitetura-visual-estudio-antigravity',
    contentMd: `A identidade visual de uma rede de blogs não se resume a escolher duas cores complementares. Ela envolve tipografia editorial, comportamento de bordas, contraste em modo escuro e responsividade milimétrica.

Confira na galeria interativa acima os registros visuais de nossos terminais e arquiteturas de servidores. Clique em qualquer imagem para abrir o modo Lightbox expandido em alta resolução com legendas técnicas detalhadas.`,
    coverImage: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1200&q=80',
    postType: 'photo_gallery',
    mediaPayload: JSON.stringify({
      galleryTitle: '📸 Galeria Exclusiva: Bastidores & Cobertura Visual',
      photos: [
        {
          url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1000&q=80',
          caption: 'Arquitetura neural abstrata representando o processamento de dados do protocolo Colmeia.',
          credit: 'Foto: Studio Antigravity'
        },
        {
          url: 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&w=1000&q=80',
          caption: 'Terminais de controle e monitoramento contínuo em tempo real na base de operações.',
          credit: 'Foto: Tech Fleet'
        },
        {
          url: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1000&q=80',
          caption: 'Linhas de código criptografadas e fluxos assíncronos gerados pela IA.',
          credit: 'Foto: Cyber Grid'
        },
        {
          url: 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?auto=format&fit=crop&w=1000&q=80',
          caption: 'Estúdio de gravação audiovisual com setup de alta performance para canais dark.',
          credit: 'Foto: Dark Trap Radio'
        }
      ]
    })
  },
  {
    id: 'post-timeline-' + Date.now(),
    title: '⏱️ Linha do Tempo: Como a Nova Diretriz de IA Regulamentou a Frota Global',
    slug: 'linha-tempo-como-nova-diretriz-ia-regulamentou-frota-global',
    contentMd: `Em jornalismo investigativo e na cobertura de notícias dinâmicas, os fatos não acontecem no vácuo. Cada nova declaração pública ou movimento de mercado está intimamente ligado aos acontecimentos dos dias anteriores.

Na linha do tempo interativa acima, mapeamos a correlação cronológica exata das últimas decisões do setor de tecnologia e inteligência artificial. Clique em cada ponto da linha para expandir os resumos analíticos e compreender a evolução completa da matéria.`,
    coverImage: 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80',
    postType: 'news_timeline',
    mediaPayload: JSON.stringify({
      timelineTitle: '⏱️ Linha do Tempo: Correlação de Fatos & Evolução da Notícia',
      nodes: [
        {
          timeLabel: 'Ontem · 14:30',
          title: 'Primeiro Alerta do Banco Central',
          summary: 'Comunicado oficial aponta para necessidade de regulamentação imediata de protocolos descentralizados e inteligência autônoma.',
          tag: 'Origem',
          isHighlight: false
        },
        {
          timeLabel: 'Hoje · 08:00',
          title: 'Reação dos Mercados & Ações Tech',
          summary: 'Bolsas asiáticas e europeias abrem em alta puxadas pelo setor de semicondutores e servidores de processamento neural.',
          tag: 'Mercado',
          isHighlight: false
        },
        {
          timeLabel: 'Hoje · 11:45',
          title: 'Pronunciamento Conjunto da Frota Antigravity',
          summary: 'A diretoria da rede confirma a sincronização total da colmeia e o acionamento de relatórios em tempo real sem falhas de memória.',
          tag: 'Breaking',
          isHighlight: true
        },
        {
          timeLabel: 'Agora · Em Andamento',
          title: 'Implementação de Módulos Interativos no CMS',
          summary: 'Deploy ao vivo da arquitetura que permite a cada site exibir players, galerias e timelines geradas autonomamente por IA.',
          tag: 'Evolução',
          isHighlight: true
        }
      ]
    })
  }
];

const insertStmt = db.prepare(`
  INSERT OR REPLACE INTO Post (
    id, title, slug, contentMd, contentHtml, coverImage, author, isPublished, publishedAt, createdAt, updatedAt, blogId, categoryId, views, language, postType, mediaPayload
  ) VALUES (
    ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, 'pt', ?, ?
  )
`);

const linkCatStmt = db.prepare(`INSERT OR IGNORE INTO PostCategory (postId, categoryId) VALUES (?, ?)`);

posts.forEach(p => {
  insertStmt.run(
    p.id, p.title, p.slug, p.contentMd, `<p>${p.contentMd}</p>`, p.coverImage, 'Diretoria Executiva', now, now, now, blog.id, category.id, 142, p.postType, p.mediaPayload
  );
  linkCatStmt.run(p.id, category.id);
  console.log(`✓ Post interativo criado: [${p.postType}] ${p.title}`);
});

db.close();
console.log('Todos os 4 posts de demonstração interativa foram injetados com sucesso!');
