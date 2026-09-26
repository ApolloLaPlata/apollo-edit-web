const Database = require('better-sqlite3');
const { Pool } = require('pg');
const fs = require('fs');

async function migrate() {
  if (!process.env.DATABASE_URL) {
    console.error("ERRO: Variável DATABASE_URL não definida. Defina a string de conexão do PostgreSQL (Supabase/Neon).");
    process.exit(1);
  }

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false }
  });

  const sqlite = new Database('dev.db');
  
  console.log("🚀 Iniciando migração de dev.db para PostgreSQL...");

  // 1. Criar tabelas
  console.log("📦 Lendo esquema original...");
  const tables = sqlite.prepare("SELECT name, sql FROM sqlite_master WHERE type='table'").all();
  
  for (const table of tables) {
    if (table.name === 'sqlite_sequence' || !table.sql) continue;
    
    // Converte a sintaxe do SQLite para PostgreSQL (básico)
    let pgSql = table.sql
      .replace(/AUTOINCREMENT/ig, '')
      .replace(/INTEGER PRIMARY KEY/ig, 'SERIAL PRIMARY KEY')
      .replace(/DATETIME/ig, 'TIMESTAMP')
      .replace(/REAL/ig, 'NUMERIC');
      
    try {
      await pool.query(pgSql);
      console.log(`✅ Tabela ${table.name} criada.`);
    } catch (e) {
      console.log(`⚠️ Aviso ao criar tabela ${table.name}: ${e.message}`);
    }
  }

  // 2. Migrar dados
  for (const table of tables) {
    if (table.name === 'sqlite_sequence' || !table.sql) continue;
    
    const rows = sqlite.prepare(`SELECT * FROM "${table.name}"`).all();
    if (rows.length === 0) continue;

    console.log(`🔄 Migrando ${rows.length} registros da tabela ${table.name}...`);
    
    const cols = Object.keys(rows[0]);
    const colNames = cols.map(c => `"${c}"`).join(', ');
    const placeholders = cols.map((_, i) => `$${i + 1}`).join(', ');
    const insertQuery = `INSERT INTO "${table.name}" (${colNames}) VALUES (${placeholders})`;

    for (const row of rows) {
      const values = cols.map(c => row[c]);
      try {
        await pool.query(insertQuery, values);
      } catch (e) {
        // Ignora duplicatas
        if (!e.message.includes('duplicate key')) {
          console.error(`Erro ao inserir na tabela ${table.name}:`, e.message);
        }
      }
    }
    console.log(`✅ Tabela ${table.name} migrada com sucesso.`);
  }

  console.log("🎉 Migração concluída com sucesso!");
  process.exit(0);
}

migrate();
