const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(process.cwd(), 'dev.db');
const db = new Database(dbPath);

console.log('Iniciando migração de variáveis de Layout Inteligente (Fase 67)...');

try {
  // Tentar adicionar colunas estéticas à tabela Blog
  await db.prepare(`ALTER TABLE Blog ADD COLUMN primaryColor TEXT DEFAULT '#3b82f6'`).run();
  console.log('Coluna primaryColor adicionada.');
} catch (e) {
  console.log('Coluna primaryColor já existe ou erro:', e.message);
}

try {
  await db.prepare(`ALTER TABLE Blog ADD COLUMN secondaryColor TEXT DEFAULT '#1e40af'`).run();
  console.log('Coluna secondaryColor adicionada.');
} catch (e) {
  console.log('Coluna secondaryColor já existe ou erro:', e.message);
}

try {
  await db.prepare(`ALTER TABLE Blog ADD COLUMN layoutStyle TEXT DEFAULT 'magazine'`).run();
  console.log('Coluna layoutStyle adicionada.');
} catch (e) {
  console.log('Coluna layoutStyle já existe ou erro:', e.message);
}

console.log('Migração concluída com sucesso!');
