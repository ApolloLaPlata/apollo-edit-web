const db = require('better-sqlite3')('dev.db');
const tables = await db.prepare("SELECT name, sql FROM sqlite_master WHERE type='table'").all();
console.log(JSON.stringify(tables, null, 2));
