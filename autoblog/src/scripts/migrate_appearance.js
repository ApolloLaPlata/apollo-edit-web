const db = require('./node_modules/better-sqlite3')('./dev.db');

const migrations = [
  "ALTER TABLE Blog ADD COLUMN fontFamily TEXT DEFAULT 'inter'",
  "ALTER TABLE Blog ADD COLUMN logoUrl TEXT DEFAULT ''",
  "ALTER TABLE Blog ADD COLUMN accentStyle TEXT DEFAULT 'rounded'",
];

migrations.forEach((sql) => {
  try {
    await db.prepare(sql).run();
    const match = sql.match(/ADD COLUMN (\w+)/);
    console.log('OK:', match ? match[1] : sql);
  } catch (e) {
    const match = sql.match(/ADD COLUMN (\w+)/);
    console.log('Skip (exists):', match ? match[1] : e.message);
  }
});

const cols = await db.prepare('PRAGMA table_info(Blog)').all();
console.log('\nBlog columns:', cols.map(c => c.name).join(', '));
db.close();
