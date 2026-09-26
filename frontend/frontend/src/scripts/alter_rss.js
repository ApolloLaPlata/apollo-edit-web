const Database = require('better-sqlite3');
const path = require('path');

const db = new Database(path.join(__dirname, 'dev.db'));

try {
  // Tentar adicionar a coluna rssFeeds
  db.prepare(`ALTER TABLE AgentConfig ADD COLUMN rssFeeds TEXT`).run();
  console.log('✅ Coluna rssFeeds adicionada com sucesso na tabela AgentConfig!');
  
  // Injetar alguns Feeds RSS de teste no blog Filosofia do Código e Tutorial das Coisas
  // Filosofia do Código (blogId 2 no array de seed, ou buscar por domain)
  const blog = db.prepare('SELECT id FROM Blog WHERE domain = ?').get('filosofiadocodigo.com');
  if (blog) {
    db.prepare('UPDATE AgentConfig SET rssFeeds = ? WHERE blogId = ?').run('https://g1.globo.com/rss/g1/tecnologia/', blog.id);
    console.log('✅ Feed G1 Tecnologia injetado no Filosofia do Código!');
  }

} catch (error) {
  if (error.message.includes('duplicate column name')) {
    console.log('⚠️ A coluna rssFeeds já existe!');
  } else {
    console.error('❌ Erro:', error);
  }
}
