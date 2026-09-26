const path = require('path');
const dbPath = path.resolve(__dirname, '../dev.db');
const db = require('better-sqlite3')(dbPath);
const result = db.prepare("PRAGMA table_info('Post')").all();
console.log(result);
