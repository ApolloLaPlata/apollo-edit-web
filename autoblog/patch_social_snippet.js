const db = require('better-sqlite3')('dev.db');

try {
  db.prepare("ALTER TABLE SocialSnippet ADD COLUMN isPublished BOOLEAN DEFAULT 0").run();
  console.log("Coluna isPublished adicionada à tabela SocialSnippet com sucesso.");
} catch (e) {
  if (e.message.includes('duplicate column name')) {
    console.log("Coluna isPublished já existe na tabela SocialSnippet.");
  } else {
    console.error("Erro ao alterar a tabela:", e.message);
  }
}
