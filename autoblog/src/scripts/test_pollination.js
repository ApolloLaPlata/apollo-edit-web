const Database = require('better-sqlite3');
const path = require('path');
const db = new Database(path.join(__dirname, 'dev.db'));

await db.prepare(`INSERT OR IGNORE INTO Blog (id, name, domain, niche, updatedAt) VALUES ('blog-fake-2', 'Descarga News', 'descarga.com', 'Fofoca', datetime('now'))`).run();

await db.prepare(`INSERT OR IGNORE INTO Post (id, blogId, title, slug, contentMd, views, isPublished, createdAt) VALUES ('post-fake-2', 'blog-fake-2', 'Fofoca viral: Ator perde tudo em ações', 'fofoca-viral', 'Conteudo falso', 5000, 1, datetime('now'))`).run();

console.log("Mock data inserted!");
