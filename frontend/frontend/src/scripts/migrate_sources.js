const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(__dirname, 'dev.db');
const db = new Database(dbPath);

console.log('Iniciando Migração V5: Criação do ContentSource...');

try {
  db.prepare(`
    CREATE TABLE IF NOT EXISTS ContentSource (
      id TEXT PRIMARY KEY,
      blogId TEXT NOT NULL,
      name TEXT NOT NULL,
      rssUrl TEXT NOT NULL,
      niche TEXT DEFAULT 'geral',
      isActive INTEGER DEFAULT 1,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (blogId) REFERENCES Blog(id) ON DELETE CASCADE
    )
  `).run();
  console.log('✔ Tabela ContentSource criada com sucesso!');

  // Injetar Fontes Padrão Iniciais para o Blog Principal
  const blog = db.prepare('SELECT id FROM Blog LIMIT 1').get();
  
  if (blog) {
    const checkSource = db.prepare('SELECT COUNT(*) as count FROM ContentSource').get();
    if (checkSource.count === 0) {
      const insert = db.prepare(`INSERT INTO ContentSource (id, blogId, name, rssUrl, niche) VALUES (?, ?, ?, ?, ?)`);
      
      insert.run('src_1', blog.id, 'BBC News Brasil', 'https://feeds.bbci.co.uk/portuguese/rss.xml', 'noticias');
      insert.run('src_2', blog.id, 'Jovem Nerd', 'https://jovemnerd.com.br/feed/', 'tecnologia');
      insert.run('src_3', blog.id, 'Google Trends', 'https://trends.google.com.br/trending/rss?geo=BR', 'geral');
      insert.run('src_4', blog.id, 'Wired', 'https://www.wired.com/feed/rss', 'tecnologia');

      console.log('✔ 4 Fontes de Matéria-Prima injetadas no banco de dados!');
    } else {
      console.log('ℹ️ Fontes já cadastradas no banco.');
    }
  }

} catch (err) {
  console.error('❌ Erro na migração:', err);
} finally {
  db.close();
}
