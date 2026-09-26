const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Configurações do ambiente
const ORACLE_BRIDGE_KEY = process.env.ORACLE_BRIDGE_KEY;
const ORACLE_SERVER_URL = process.env.ORACLE_SERVER_URL || 'http://localhost:3000';
const SYNC_ENDPOINT = `${ORACLE_SERVER_URL}/api/admin/bridge/sync`;
const LOCAL_DB_PATH = path.join(__dirname, 'dev.db');

async function syncPull() {
  console.log(`[PULL] ⬇️ Solicitando download do banco de dados remoto (${ORACLE_SERVER_URL})...`);
  
  if (!ORACLE_BRIDGE_KEY) {
    console.error('❌ ERRO: Variável ORACLE_BRIDGE_KEY não definida no .env local.');
    process.exit(1);
  }

  try {
    const res = await fetch(SYNC_ENDPOINT, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${ORACLE_BRIDGE_KEY}`
      }
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`❌ ERRO NA NUVEM: ${res.status} - ${errorText}`);
      process.exit(1);
    }

    const arrayBuffer = await res.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);
    
    // Fazer backup local antes de substituir
    if (fs.existsSync(LOCAL_DB_PATH)) {
      const backupPath = path.join(__dirname, `dev_local_backup_${Date.now()}.db`);
      fs.copyFileSync(LOCAL_DB_PATH, backupPath);
      console.log(`[+] Backup local criado: ${path.basename(backupPath)}`);
    }

    fs.writeFileSync(LOCAL_DB_PATH, buffer);
    console.log(`✅ SUCESSO! dev.db atualizado com os dados da nuvem. (${buffer.length} bytes)`);

  } catch (error) {
    console.error(`❌ ERRO FATAL NO PULL:`, error.message);
  }
}

async function syncPush() {
  console.log(`[PUSH] ⬆️ Enviando banco de dados local para a nuvem (${ORACLE_SERVER_URL})...`);
  
  if (!ORACLE_BRIDGE_KEY) {
    console.error('❌ ERRO: Variável ORACLE_BRIDGE_KEY não definida no .env local.');
    process.exit(1);
  }

  if (!fs.existsSync(LOCAL_DB_PATH)) {
    console.error('❌ ERRO: Arquivo dev.db local não encontrado.');
    process.exit(1);
  }

  try {
    const fileBuffer = fs.readFileSync(LOCAL_DB_PATH);
    
    const res = await fetch(SYNC_ENDPOINT, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${ORACLE_BRIDGE_KEY}`,
        'Content-Type': 'application/octet-stream'
      },
      body: fileBuffer
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error(`❌ ERRO NA NUVEM: ${res.status} - ${errorText}`);
      process.exit(1);
    }

    const data = await res.json();
    console.log(`✅ SUCESSO!`, data.message);

  } catch (error) {
    console.error(`❌ ERRO FATAL NO PUSH:`, error.message);
  }
}

// CLI Engine
const args = process.argv.slice(2);

if (args.includes('--pull')) {
  syncPull();
} else if (args.includes('--push')) {
  syncPush();
} else {
  console.log(`
🚀 Oracle Antigravity Bridge (CLI)

Uso:
  node oracle_sync.js --pull    (Baixa o banco da Nuvem para o Local)
  node oracle_sync.js --push    (Envia o banco Local para a Nuvem)

Certifique-se de configurar ORACLE_BRIDGE_KEY e ORACLE_SERVER_URL no .env!
  `);
}
