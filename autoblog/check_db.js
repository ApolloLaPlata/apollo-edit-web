const db = require('better-sqlite3')('dev.db');
const table = db.prepare("SELECT sql FROM sqlite_master WHERE type='table' AND name='AffiliateLink'").get();
console.log("AffiliateLink Table:", table ? table.sql : 'Nao existe');
