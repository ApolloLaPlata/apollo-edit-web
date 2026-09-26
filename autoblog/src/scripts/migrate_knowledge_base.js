const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(__dirname, '../../dev.db');
const db = new Database(dbPath);

console.log("🧠 Iniciando migração da Base de Conhecimento RAG (Vector Data)...");

try {
  // Criando a tabela de Conhecimento que vai alimentar as Mentes Sêniores do Autoblog
  await db.exec(`
    CREATE TABLE IF NOT EXISTS knowledge_base (
      id TEXT PRIMARY KEY,
      channelId TEXT NOT NULL,         -- Nome do canal ou nicho (Ex: 'Descarga News', 'Global')
      sourceName TEXT NOT NULL,        -- Nome do arquivo de origem (Ex: 'MEMORIA_ATIVA_SISTEMA.md')
      content TEXT NOT NULL,           -- O parágrafo/trecho legível
      embedding TEXT NOT NULL,         -- O array numérico [0.03, -0.01...] salvo como JSON String
      createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Opcional: Índice para buscar mais rapidamente todos os contextos de um canal específico
  await db.exec(`CREATE INDEX IF NOT EXISTS idx_channel ON knowledge_base (channelId)`);

  console.log("✅ Tabela 'knowledge_base' criada com sucesso! O cérebro vetorial do Apollo Blog nasceu.");
} catch (error) {
  console.error("❌ Erro ao criar a tabela:", error.message);
}

db.close();
