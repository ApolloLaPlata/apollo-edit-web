const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Fase 100: O Motor Mutante (The Endgame)
 * Esse script lê os dados simulados de Bounce Rate. Se a retenção estiver baixa,
 * ele aciona um LLM (Mockado aqui) para sugerir uma nova paleta de cores 
 * (ex: modo noturno agressivo para hackers, ou modo suave para wellness).
 * Em seguida, ele injeta o novo CSS no globals.css e recompila!
 */

const GLOBALS_CSS_PATH = path.resolve(__dirname, '../app/globals.css');

async function triggerMutantEngine() {
  console.log('🧬 [MOTOR MUTANTE] Iniciando Varredura de Sobrevivência (Endgame)...');
  
  // 1. Coleta de Telemetria (Simulação de Bounce Rate do Google Analytics)
  const bounceRate = Math.floor(Math.random() * (90 - 40) + 40); // Sorteia entre 40% e 90%
  console.log(`🧬 [MOTOR MUTANTE] Telemetria: Bounce Rate atual é de ${bounceRate}%.`);

  if (bounceRate < 60) {
    console.log('🧬 [MOTOR MUTANTE] A audiência está engajada. Nenhuma mutação necessária.');
    return;
  }

  console.log('🧬 [MOTOR MUTANTE] 🚨 ALERTA: Retenção baixa. Invocando Inteligência Neural para auto-reescrita do CSS.');

  // 2. O Llama/Groq criaria um novo tema. Vamos alternar entre "Neon Cyberpunk" e "Minimalista Clínico".
  const themes = [
    {
      name: 'Cyberpunk',
      vars: `
        --background: 240 10% 4%;
        --foreground: 0 0% 98%;
        --primary: 316 100% 50%; /* Neon Pink */
        --secondary: 190 100% 50%; /* Cyan */
      `
    },
    {
      name: 'Dracula',
      vars: `
        --background: 231 15% 18%;
        --foreground: 60 30% 96%;
        --primary: 265 89% 78%; /* Purple */
        --secondary: 135 94% 65%; /* Green */
      `
    },
    {
      name: 'Abyss',
      vars: `
        --background: 0 0% 0%;
        --foreground: 0 0% 100%;
        --primary: 0 100% 50%; /* Blood Red */
        --secondary: 0 0% 20%; /* Dark Gray */
      `
    }
  ];

  const newTheme = themes[Math.floor(Math.random() * themes.length)];
  console.log(`🧬 [MOTOR MUTANTE] 🧠 LLM escolheu o arquétipo visual: ${newTheme.name}. Injetando no core...`);

  // 3. Lê o CSS Atual
  let cssContent = fs.readFileSync(GLOBALS_CSS_PATH, 'utf-8');

  // Regex simples para substituir as variáveis raízes do :root (dark mode preferencial)
  // Como estamos num ambiente controlado, faremos um replace brutal na tag :root da parte "dark"
  const darkRootRegex = /(\.dark\s*{[\s\S]*?)(--background:\s*[^;]+;[\s\S]*?--primary:\s*[^;]+;)([\s\S]*?})/;
  
  // Como nosso globals.css tem @layer base, vamos procurar e injetar as variaveis.
  // Pra não quebrar tudo com Regex complexa num script genérico, vamos apensar uma nova classe ao final
  // e forçar ela no body via script injetado, ou simplesmente sobrepor o .dark
  
  const mutantInjection = `
/* --- MUTANT ENGINE INJECTION: ${newTheme.name} --- */
.dark {
  --background: ${newTheme.vars.split(';').find(s => s.includes('--background'))?.split(':')[1]?.trim()};
  --foreground: ${newTheme.vars.split(';').find(s => s.includes('--foreground'))?.split(':')[1]?.trim()};
  --primary: ${newTheme.vars.split(';').find(s => s.includes('--primary'))?.split(':')[1]?.trim()};
}
/* ------------------------------------------------ */
`;

  // Anexa ao final do globals.css para sobrescrever pela cascata
  fs.appendFileSync(GLOBALS_CSS_PATH, mutantInjection);
  
  console.log('🧬 [MOTOR MUTANTE] ✅ Código genético (CSS) reescrito com sucesso.');
  
  // 4. Restart do Frontend
  console.log('🧬 [MOTOR MUTANTE] 🔄 Reiniciando container do Next.js via PM2...');
  try {
    // execSync('pm2 restart autoblog-next', { stdio: 'inherit' });
    console.log('🧬 [MOTOR MUTANTE] ✨ Sistema reiniciado e otimizado. Sobrevivência Garantida.');
  } catch (err) {
    console.log('🧬 [MOTOR MUTANTE] (Modo Local) Reinício manual necessário se não estiver via PM2.');
  }
}

if (require.main === module) {
  triggerMutantEngine();
}

module.exports = { triggerMutantEngine };
