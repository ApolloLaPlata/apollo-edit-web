const db = require('better-sqlite3')('dev.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS WebStory (
    id TEXT PRIMARY KEY,
    blogId TEXT,
    title TEXT,
    videoUrl TEXT,
    imageUrl TEXT,
    content TEXT,
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(blogId) REFERENCES Blog(id)
  );
`);

// Injetar dados Mock
const blog = db.prepare('SELECT id FROM Blog LIMIT 1').get();
if (blog) {
  const stmt = db.prepare('INSERT OR IGNORE INTO WebStory (id, blogId, title, imageUrl, content) VALUES (?, ?, ?, ?, ?)');
  stmt.run('s1', blog.id, 'O futuro do Bitcoin', 'https://images.pexels.com/photos/8370752/pexels-photo-8370752.jpeg?auto=compress&cs=tinysrgb&w=800', 'Descubra como o Bitcoin ultrapassou a barreira dos 100k e o que esperar do próximo halving.');
  stmt.run('s2', blog.id, 'Mercado Imobiliário em Alta', 'https://images.pexels.com/photos/323780/pexels-photo-323780.jpeg?auto=compress&cs=tinysrgb&w=800', 'Mercado imobiliário aquece nas capitais. É hora de investir ou esperar a queda dos juros?');
  stmt.run('s3', blog.id, 'Evolução Tecnológica', 'https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg?auto=compress&cs=tinysrgb&w=800', 'O avanço veloz das infraestruturas de computação na nuvem e o que esperar para o próximo ano.');
  console.log('Stories criados com sucesso!');
} else {
  console.log('Nenhum blog encontrado.');
}
