const { execSync } = require('child_process');
const { triggerMutantEngine } = require('./mutant_css');

console.log('🦾 [DAEMON] Serviço de Background iniciado.');

// Cron improvisado a cada 1 hora para simular a Mutação Endêmica e os publicadores
setInterval(() => {
  console.log('🦾 [DAEMON] Acordando para ciclo de auto-otimização...');
  
  // Roda a Fase 100: Motor Mutante
  triggerMutantEngine();
  
  // Tenta publicar redes sociais (Fase 7)
  try {
    execSync('node src/scripts/social_publisher.js', { stdio: 'inherit' });
  } catch(e) {
    console.log('Erro no social publisher: ', e.message);
  }
  
}, 3600000); // 1 Hora
