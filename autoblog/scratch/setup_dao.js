const db = require('better-sqlite3')('dev.db');
db.prepare(`CREATE TABLE IF NOT EXISTS DaoTopic (
  id TEXT PRIMARY KEY,
  title TEXT,
  description TEXT,
  votes INTEGER DEFAULT 0,
  status TEXT DEFAULT 'pending',
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
)`).run();
console.log('Tabela DAO Criada');

// Inserir algumas pautas iniciais para demonstração
try {
  db.prepare(`INSERT INTO DaoTopic (id, title, description) VALUES ('1', 'Exclusivo: O Impacto da IA no Mercado Imobiliário', 'Investigar como algoritmos estão comprando casas antes de humanos.')`).run();
  db.prepare(`INSERT INTO DaoTopic (id, title, description) VALUES ('2', 'Deepfakes na Política de 2026', 'Como vídeos hiper-realistas vão mudar as eleições.')`).run();
} catch(e) {}
