const path = require('path');
const dbPath = path.resolve(__dirname, '../dev.db');
const db = require('better-sqlite3')(dbPath);

console.log('📦 Executando Migração Fase 104 (Audio/Video)...');

try {
  // Adiciona a coluna audioUrl
  db.exec(`ALTER TABLE Post ADD COLUMN audioUrl TEXT`);
  console.log('✅ Coluna audioUrl criada na tabela Post');
} catch (e) {
  if (e.message.includes('duplicate column name')) {
    console.log('⚠️ Coluna audioUrl já existe.');
  } else {
    console.error('Erro na audioUrl:', e.message);
  }
}

try {
  // Adiciona a coluna videoUrl
  db.exec(`ALTER TABLE Post ADD COLUMN videoUrl TEXT`);
  console.log('✅ Coluna videoUrl criada na tabela Post');
} catch (e) {
  if (e.message.includes('duplicate column name')) {
    console.log('⚠️ Coluna videoUrl já existe.');
  } else {
    console.error('Erro na videoUrl:', e.message);
  }
}

console.log('🏁 Migração Concluída.');
