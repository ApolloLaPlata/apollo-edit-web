const fs = require('fs');
const path = require('path');

const templatesDir = path.join(__dirname, 'src/components/blog/templates');
const files = fs.readdirSync(templatesDir).filter(f => f.endsWith('.tsx'));

const replacements = [
  // 1. Limpeza de IA e Robôs
  { pattern: /revisado pela IA/gi, replace: 'revisado pela Equipe Especializada' },
  { pattern: /INTELIGÊNCIA EDITORIAL/g, replace: 'REDAÇÃO VIP' },
  { pattern: /Inteligência Editorial/gi, replace: 'Equipe de Jornalistas' },
  { pattern: /Frequência IA/gi, replace: 'Frequência de Pautas' },
  { pattern: /POR IA/g, replace: 'PELA REDAÇÃO' },
  { pattern: /pela Inteligência/gi, replace: 'pela Redação' },
  { pattern: /REDAÇÃO AUTÔNOMA IA/g, replace: 'REDAÇÃO ESPECIALIZADA' },
  { pattern: /REDAÇÃO AUTÔNOMA/g, replace: 'REDAÇÃO VIP' },
  { pattern: /Redação Autônoma/gi, replace: 'Redação VIP' },
  { pattern: /Redação Autônomo/gi, replace: 'Redação VIP' },
  { pattern: /em IA/g, replace: 'Tecnológicos' },
  { pattern: /autônoma/gi, replace: 'independente' },
  { pattern: /Áudio IA/gi, replace: 'Áudio Pro' },
  { pattern: /INTELIGÊNCIA ARTIFICIAL/g, replace: 'EQUIPE AUDIOVISUAL' },
  { pattern: /nossa IA/gi, replace: 'nossa Redação' },
  { pattern: /análises de IA/gi, replace: 'análises de especialistas' },

  // 2. Mascaramento Dinâmico de Autor (Se post.author estiver sendo renderizado puro)
  { 
    pattern: /\{post\.author\}/g, 
    replace: "{(post.author || '').replace(/Redação IA/gi, post.blog_name || 'Equipe Especial') || post.blog_name || 'Redação'}" 
  },
  { 
    pattern: /\{post\.author \|\| 'Redação'\}/g, 
    replace: "{(post.author || '').replace(/Redação IA/gi, post.blog_name || 'Equipe Especial') || post.blog_name || 'Redação'}" 
  },
  {
    pattern: /\{post\.author \? \`por \$\{post\.author\}\` : ''\}/g,
    replace: "{post.author ? `por ${(post.author || '').replace(/Redação IA/gi, post.blog_name || 'Equipe Especial')}` : ''}"
  },

  // 3. Melhoria Visual - Injetar Glassmorphism e Cores Premium em Headers duros (Slate-900 / Bg-White)
  {
    pattern: /bg-slate-900 border-b border-slate-800/g,
    replace: "bg-gradient-to-b from-slate-950 to-slate-900 border-b border-theme-border/50 backdrop-blur-md"
  },
  {
    pattern: /bg-white border-b border-gray-100/g,
    replace: "bg-white/80 backdrop-blur-xl border-b border-gray-200/50 shadow-sm"
  }
];

let changedFiles = 0;

for (const file of files) {
  const filePath = path.join(templatesDir, file);
  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;

  for (const { pattern, replace } of replacements) {
    content = content.replace(pattern, replace);
  }

  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`Template atualizado: ${file}`);
    changedFiles++;
  }
}

console.log(`\nRefatoração Concluída. ${changedFiles} templates limpos e melhorados visualmente.`);
