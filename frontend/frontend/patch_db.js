const Database = require('better-sqlite3');
const path = require('path');
const dbPath = path.resolve(__dirname, 'dev.db');
const db = new Database(dbPath);

console.log('Iniciando migração do Banco de Dados SQLite...');

try {
  db.prepare(`ALTER TABLE Post ADD COLUMN status TEXT DEFAULT 'published'`).run();
  console.log('✅ Coluna "status" adicionada na tabela Post.');
} catch (e) {
  if (e.message.includes('duplicate column name')) {
    console.log('ℹ️ Coluna "status" já existe na tabela Post.');
  } else {
    console.error('❌ Erro ao adicionar coluna "status":', e.message);
  }
}

try {
  db.prepare(`ALTER TABLE Post ADD COLUMN summary TEXT`).run();
  console.log('✅ Coluna "summary" adicionada na tabela Post.');
} catch (e) {
  if (e.message.includes('duplicate column name')) {
    console.log('ℹ️ Coluna "summary" já existe na tabela Post.');
  } else {
    console.error('❌ Erro ao adicionar coluna "summary":', e.message);
  }
}

console.log('Migração concluída.');
