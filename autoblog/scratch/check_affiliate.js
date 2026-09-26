const fs = require('fs');
const path = require('path');
const dbPath = path.resolve(__dirname, '../dev.db');
const db = require('better-sqlite3')(dbPath);

try {
  const result = db.prepare("PRAGMA table_info('AffiliateLink')").all();
  console.log(result);
} catch (e) {
  console.error(e.message);
}
