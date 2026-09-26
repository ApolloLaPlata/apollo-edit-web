const fs = require('fs');
const path = require('path');
const dbPath = path.resolve(__dirname, '../dev.db');
const db = require('better-sqlite3')(dbPath);
const { execSync } = require('child_process');

/**
 * Fase 85: Agentes Competitivos (Guerra de IA)
 * Este script simula a competição entre satélites.
 * Ele pega as keywords da tabela Trend, e distribui entre os blogs.
 * Blogs diferentes tentarão publicar sobre o mesmo assunto ao mesmo tempo,
 * com um pequeno "delay" artificial para simular quem chegou primeiro e levou a exclusividade.
 */

console.log('⚔️ [AI WAR] Iniciando simulação de agentes competitivos...');

try {
  // Pega uma trend pendente (se não houver, pega uma keyword aleatória do Planner)
  let trend = db.prepare(`SELECT * FROM PlannerKeyword WHERE status = 'pending' ORDER BY searchVolume DESC LIMIT 1`).get();
  
  if (!trend) {
    console.log('⚔️ [AI WAR] Nenhuma pauta de alto tráfego no Radar.');
    process.exit(0);
  }

  // Seleciona 2 a 3 blogs aleatórios para competirem pela pauta
  const combatants = db.prepare(`SELECT id, name, domain FROM Blog ORDER BY RANDOM() LIMIT 3`).all();
  
  if (combatants.length < 2) {
    console.log('⚔️ [AI WAR] Não há blogs suficientes para uma guerra de tráfego. (Mínimo 2)');
    process.exit(0);
  }

  console.log(`🔥 [AI WAR] Nova pauta sangrenta: "${trend.keyword}" (Volume: ${trend.searchVolume})`);
  console.log(`🔥 [AI WAR] Combatentes: ${combatants.map(c => c.name).join(' vs ')}`);

  // O primeiro a terminar (menor tempo randomico) ganha o bônus de "Exclusividade" ou publica de fato.
  // Como estamos no script, vamos disparar a geração (simulando a fila)
  combatants.forEach(blog => {
    const delay = Math.floor(Math.random() * 10000); // 0 a 10s
    setTimeout(() => {
      console.log(`🚀 [AI WAR] O Agente do blog [${blog.name}] disparou o gerador de artigos para a keyword "${trend.keyword}"!`);
      // Aqui em produção integraríamos com a fila do RabbitMQ ou chamada de API
      // Para simular, chamamos o CLI de seed_impire.js ou gerador.
      try {
        // Marcamos a trend como processada para o primeiro que atirar
        const currentTrend = db.prepare(`SELECT status FROM PlannerKeyword WHERE id = ?`).get(trend.id);
        if (currentTrend.status === 'pending') {
          db.prepare(`UPDATE PlannerKeyword SET status = 'in_progress' WHERE id = ?`).run(trend.id);
          console.log(`🏆 [AI WAR] ${blog.name} pegou a exclusividade (First Mover Advantage)!`);
          
          // Inserimos a task de geração no banco pro daemon pegar
          db.prepare(`
            INSERT INTO GenerationTask (blogId, sourceUrl, prompt, status, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
          `).run(blog.id, '', `Escreva uma notícia bombástica e exclusiva sobre: ${trend.keyword}. Tema do Blog: ${blog.name}`, 'pending');
          
        } else {
          console.log(`💨 [AI WAR] ${blog.name} chegou tarde. Fará apenas uma matéria de cobertura secundária.`);
        }
      } catch (err) {
        console.error(`Erro no combate do ${blog.name}:`, err.message);
      }
    }, delay);
  });

} catch (err) {
  console.error('Erro Fatal na Guerra de IA:', err);
}
