const db = require('better-sqlite3')('dev.db');

try {
  await db.exec(`CREATE TABLE IF NOT EXISTS AffiliateClick (
    id TEXT PRIMARY KEY,
    blogId TEXT NOT NULL,
    postId TEXT,
    affiliateLinkId TEXT,
    linkUrl TEXT NOT NULL,
    linkLabel TEXT,
    clickedAt TEXT DEFAULT (datetime('now')),
    ipHash TEXT,
    country TEXT DEFAULT 'BR',
    revenue REAL DEFAULT 0
  )`);
  console.log('AffiliateClick criado.');
} catch(e) { console.log('AffiliateClick:', e.message); }

try { await db.exec("ALTER TABLE AffiliateLink ADD COLUMN trackingCode TEXT"); console.log('trackingCode ok'); } catch(e) { console.log(e.message); }
try { await db.exec("ALTER TABLE AffiliateLink ADD COLUMN estimatedCpc REAL DEFAULT 0.50"); console.log('estimatedCpc ok'); } catch(e) { console.log(e.message); }
try { await db.exec("ALTER TABLE AffiliateLink ADD COLUMN totalClicks INTEGER DEFAULT 0"); console.log('totalClicks ok'); } catch(e) { console.log(e.message); }

console.log('Migração concluída.');
