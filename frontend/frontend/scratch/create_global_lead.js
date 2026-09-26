const fs = require('fs');
const path = require('path');
const dbPath = path.resolve(__dirname, '../dev.db');
const db = require('better-sqlite3')(dbPath);

console.log('Criando tabela GlobalLead para Compartilhamento (Fase 88)...');
try {
  db.exec(`
    CREATE TABLE IF NOT EXISTS GlobalLead (
      id TEXT PRIMARY KEY,
      email TEXT UNIQUE NOT NULL,
      sourceBlogId TEXT,
      score INTEGER DEFAULT 0,
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    );
  `);
  console.log('✅ Tabela GlobalLead criada com sucesso.');
} catch (e) {
  console.error('Erro:', e.message);
}
