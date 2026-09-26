const Database = require('better-sqlite3');
const db = new Database('dev.db');
const tables = db.prepare('SELECT sql FROM sqlite_master WHERE type=\'table\'').all();
tables.forEach(t => {
  if (t.sql) console.log(t.sql + ';');
});
