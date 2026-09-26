const db = require('./node_modules/better-sqlite3')('./dev.db');

console.log('--- Migração: Adicionando coluna socialLinks em Blog ---');

try {
  await db.prepare("ALTER TABLE Blog ADD COLUMN socialLinks TEXT DEFAULT '{}'").run();
  console.log('✓ Coluna socialLinks adicionada com sucesso em Blog!');
} catch (e) {
  console.log('• Coluna socialLinks já existe em Blog:', e.message);
}

// Semear links demonstrativos no portal principal
const defaultSocials = {
  youtube: "https://www.youtube.com/@antigravity_studio",
  facebook: "https://www.facebook.com/antigravity.cms",
  instagram: "https://www.instagram.com/antigravity_ai",
  twitter: "https://x.com/antigravity_ai",
  tiktok: "https://www.tiktok.com/@antigravity_tech",
  kwai: "https://www.kwai.com/@antigravity_ai",
  dailymotion: "https://www.dailymotion.com/antigravity_studio",
  newsletter: "https://antigravity.news/subscribe"
};

const blogs = await db.prepare('SELECT id, name, domain FROM Blog').all();
for (const b of blogs) {
  await db.prepare('UPDATE Blog SET socialLinks = ? WHERE id = ?').run(JSON.stringify(defaultSocials), b.id);
  console.log(`✓ Links sociais semeados para o portal: ${b.name} (${b.domain})`);
}

db.close();
console.log('--- Migração concluída! ---');
