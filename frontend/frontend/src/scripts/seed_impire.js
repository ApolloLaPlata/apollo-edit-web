const Database = require('better-sqlite3');
const path = require('path');
const crypto = require('crypto');

const db = new Database(path.join(__dirname, 'dev.db'));

const canais = [
  {
    name: 'Dark Trap Radio',
    domain: 'darktrapradio.com',
    niche: 'Música underground, Rap, Dark Trap, Lançamentos, Curiosidades Musicais',
    personaPrompt: 'Você é um curador musical underground. Sua fala é estética, usa gírias do universo rap/trap com moderação, mas mantém um tom profundo, misterioso e crítico. Você analisa o flow, as batidas e as letras dos artistas com maestria.',
    theme: 'dark',
    primaryColor: '#7c3aed',
    layoutStyle: 'minimalist'
  },
  {
    name: 'Filosofia do Código',
    domain: 'filosofiadocodigo.com',
    niche: 'Engenharia de Software, Reflexões Tech, IA, Cultura Hacker',
    personaPrompt: 'Você é um engenheiro de software sênior que vê poesia nos algoritmos. Você escreve como um filósofo da era digital. Suas análises sobre código, IA e sociedade são profundas, lúcidas e inspiradoras.',
    theme: 'dark',
    primaryColor: '#10b981',
    layoutStyle: 'tech'
  },
  {
    name: 'História de 7 Dias',
    domain: 'historiade7dias.com',
    niche: 'Contos, Curiosidades Históricas, Mistérios, Narrativas Profundas',
    personaPrompt: 'Você é um exímio contador de histórias. Você narra mistérios e crônicas com um tom cinematográfico, de forma que o leitor não consiga parar de ler. Use técnicas de suspense, clímax e desenvolvimento de personagens históricos.',
    theme: 'dark',
    primaryColor: '#f59e0b',
    layoutStyle: 'magazine'
  },
  {
    name: 'Macaco Driver',
    domain: 'macacodriver.com',
    niche: 'Mobilidade Urbana, Carros, Motos, Mecânica, Cotidiano das Ruas',
    personaPrompt: 'Você é um motorista experiente, apaixonado por motores e pelas ruas. Você fala de mecânica, lançamentos automotivos e trânsito com a propriedade de quem vive com a mão na graxa. Seu tom é amigável, direto e prático.',
    theme: 'light',
    primaryColor: '#ef4444',
    layoutStyle: 'magazine'
  },
  {
    name: 'Tutorial das Coisas',
    domain: 'tutorialdascoisas.com',
    niche: 'Faça-você-mesmo (DIY), Lifehacks, Tutoriais de Software e Hardware, Dicas Práticas',
    personaPrompt: 'Você é um instrutor super didático e paciente. Você quebra conceitos complexos em passos extremamente simples. Seu foco é resolver a dor do leitor no menor tempo possível, sem enrolação. Use listas, tópicos e formatação clara.',
    theme: 'light',
    primaryColor: '#3b82f6',
    layoutStyle: 'classic'
  }
];

let added = 0;

try {
  db.prepare('BEGIN').run();

  const insertBlog = db.prepare(`
    INSERT INTO Blog (id, name, domain, niche, theme, primaryColor, layoutStyle, createdAt, updatedAt)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const insertAgent = db.prepare(`
    INSERT INTO AgentConfig (id, blogId, personaPrompt, imageStylePrompt, postFrequency, isActive, postIntervalHours)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);

  const checkBlog = db.prepare('SELECT id FROM Blog WHERE domain = ?');

  for (const canal of canais) {
    const existing = checkBlog.get(canal.domain);
    if (!existing) {
      const blogId = crypto.randomUUID();
      const agentId = crypto.randomUUID();
      const now = new Date().toISOString();

      insertBlog.run(
        blogId,
        canal.name,
        canal.domain,
        canal.niche,
        canal.theme,
        canal.primaryColor,
        canal.layoutStyle,
        now,
        now
      );

      insertAgent.run(
        agentId,
        blogId,
        canal.personaPrompt,
        'Estilo fotorealista, cinematográfico, cores vibrantes, ultra detalhado.',
        1,
        1, // isActive
        6  // postIntervalHours
      );

      added++;
      console.log(`[+] Adicionado: ${canal.name}`);
    } else {
      console.log(`[!] Ignorado (já existe): ${canal.name}`);
    }
  }

  db.prepare('COMMIT').run();
  console.log(`\nConcluído! ${added} novas franquias injetadas.`);
} catch (err) {
  db.prepare('ROLLBACK').run();
  console.error('Erro na injeção:', err);
}
