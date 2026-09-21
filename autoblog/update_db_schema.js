const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(process.cwd(), 'dev.db');
const db = new Database(dbPath);

console.log("Adicionando colunas na tabela Post...");

try {
  db.prepare('ALTER TABLE Post ADD COLUMN audioUrl TEXT;').run();
  console.log("Coluna audioUrl adicionada.");
} catch (e) {
  console.log("audioUrl já existe ou erro:", e.message);
}

try {
  db.prepare('ALTER TABLE Post ADD COLUMN videoUrl TEXT;').run();
  console.log("Coluna videoUrl adicionada.");
} catch (e) {
  console.log("videoUrl já existe ou erro:", e.message);
}

const tableInfo = db.prepare("PRAGMA table_info('Post')").all();
console.log("Schema da tabela Post:", tableInfo);
