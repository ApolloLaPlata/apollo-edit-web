const db = require('./node_modules/better-sqlite3')('./dev.db');

const migrations = [
  // Colunas na tabela Post
  "ALTER TABLE Post ADD COLUMN postType TEXT DEFAULT 'article'",
  "ALTER TABLE Post ADD COLUMN mediaPayload TEXT DEFAULT '{}'",
  // Coluna na tabela Blog
  "ALTER TABLE Blog ADD COLUMN activeFeatures TEXT DEFAULT '[\"article\",\"video_series\",\"audio_track\",\"photo_gallery\",\"news_timeline\"]'",
];

migrations.forEach((sql) => {
  try {
    await db.prepare(sql).run();
    const match = sql.match(/ADD COLUMN (\w+)/);
    console.log('OK:', match ? match[1] : sql);
  } catch (e) {
    const match = sql.match(/ADD COLUMN (\w+)/);
    console.log('Skip (already exists):', match ? match[1] : e.message);
  }
});

const postCols = await db.prepare('PRAGMA table_info(Post)').all();
console.log('\nPost columns:', postCols.map(c => c.name).join(', '));

const blogCols = await db.prepare('PRAGMA table_info(Blog)').all();
console.log('Blog columns:', blogCols.map(c => c.name).join(', '));

db.close();
