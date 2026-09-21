const Database = require('better-sqlite3');
const path = require('path');
const dbPath = path.resolve(process.cwd(), 'dev.db');
const db = new Database(dbPath);
const tableInfo = db.prepare("PRAGMA table_info('AgentConfig')").all();
console.log(tableInfo);
