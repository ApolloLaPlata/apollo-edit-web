const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(__dirname, '../../dev.db');
const db = new Database(dbPath);

console.log("🛠️ Iniciando a migração do Banco de Dados para Integração de Vídeo...");

try {
  // Tabela para o Motor de Exportação de Roteiros (Cross-channel)
  db.exec(`
    CREATE TABLE IF NOT EXISTS video_render_queue (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      post_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      summary TEXT NOT NULL,
      image_prompt TEXT,
      search_query TEXT,
      status TEXT DEFAULT 'pending',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
    )
  `);

  console.log("✅ Tabela 'video_render_queue' criada com sucesso! (Estágio 3 Preparado)");
} catch (error) {
  console.error("❌ Erro ao criar a tabela:", error);
}

db.close();
