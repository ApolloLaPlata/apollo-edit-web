const Database = require('better-sqlite3');
const path = require('path');

const dbPath = path.resolve(__dirname, 'dev.db');
const db = new Database(dbPath);

console.log("[MIGRATE] Iniciando a injeção do Motor de Design System Dinâmico...");

try {
  // Cores de Contraste Profundo
  await db.exec(`ALTER TABLE Blog ADD COLUMN bgPrimary TEXT DEFAULT '#020617'`);
  console.log("✔️ Coluna bgPrimary injetada.");
} catch (e) {
  console.log("⚠️ Coluna bgPrimary já existe ou falhou:", e.message);
}

try {
  await db.exec(`ALTER TABLE Blog ADD COLUMN bgSurface TEXT DEFAULT '#1e293b'`);
  console.log("✔️ Coluna bgSurface injetada.");
} catch (e) {
  console.log("⚠️ Coluna bgSurface já existe ou falhou:", e.message);
}

try {
  // Tipografia
  await db.exec(`ALTER TABLE Blog ADD COLUMN fontHeading TEXT DEFAULT 'Inter'`);
  console.log("✔️ Coluna fontHeading injetada.");
} catch (e) {
  console.log("⚠️ Coluna fontHeading já existe ou falhou:", e.message);
}

try {
  await db.exec(`ALTER TABLE Blog ADD COLUMN fontBody TEXT DEFAULT 'Inter'`);
  console.log("✔️ Coluna fontBody injetada.");
} catch (e) {
  console.log("⚠️ Coluna fontBody já existe ou falhou:", e.message);
}

try {
  // Imagens Exclusivas do Blog
  await db.exec(`ALTER TABLE Blog ADD COLUMN bannerUrl TEXT DEFAULT ''`);
  console.log("✔️ Coluna bannerUrl injetada.");
} catch (e) {
  console.log("⚠️ Coluna bannerUrl já existe ou falhou:", e.message);
}

console.log("[MIGRATE] Estrutura estendida com sucesso. O motor dinâmico pode operar!");
