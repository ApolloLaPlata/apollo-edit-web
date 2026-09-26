const Database = require('better-sqlite3');
const db = new Database('dev.db');
const schema = db.prepare(`SELECT name, sql FROM sqlite_master WHERE type='table'`).all();
console.log(JSON.stringify(schema, null, 2));
