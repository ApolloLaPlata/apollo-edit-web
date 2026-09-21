import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

// Rota de Sincronização Segura do Banco de Dados SQLite (dev.db)
export async function GET(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  const bridgeKey = process.env.ORACLE_BRIDGE_KEY;

  if (!bridgeKey) {
    return NextResponse.json({ error: 'Bridge Key não configurada no servidor' }, { status: 500 });
  }

  if (authHeader !== `Bearer ${bridgeKey}`) {
    return NextResponse.json({ error: 'Acesso Negado: Chave Quântica Inválida' }, { status: 401 });
  }

  try {
    const dbPath = path.join(process.cwd(), 'dev.db');
    if (!fs.existsSync(dbPath)) {
      return NextResponse.json({ error: 'Banco de dados não encontrado' }, { status: 404 });
    }

    const fileBuffer = fs.readFileSync(dbPath);
    return new NextResponse(fileBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': 'attachment; filename="dev.db"',
      },
    });
  } catch (error: any) {
    console.error('[BRIDGE] Erro no PULL:', error);
    return NextResponse.json({ error: 'Erro interno no servidor' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  const bridgeKey = process.env.ORACLE_BRIDGE_KEY;

  if (!bridgeKey) {
    return NextResponse.json({ error: 'Bridge Key não configurada no servidor' }, { status: 500 });
  }

  if (authHeader !== `Bearer ${bridgeKey}`) {
    return NextResponse.json({ error: 'Acesso Negado: Chave Quântica Inválida' }, { status: 401 });
  }

  try {
    const data = await request.arrayBuffer();
    if (!data || data.byteLength === 0) {
      return NextResponse.json({ error: 'Nenhum dado recebido' }, { status: 400 });
    }

    const dbPath = path.join(process.cwd(), 'dev.db');
    const backupPath = path.join(process.cwd(), `dev_backup_${Date.now()}.db`);

    // Faz um backup por segurança antes de sobrescrever
    if (fs.existsSync(dbPath)) {
      fs.copyFileSync(dbPath, backupPath);
    }

    // Sobrescreve o banco original
    fs.writeFileSync(dbPath, Buffer.from(data));

    return NextResponse.json({ success: true, message: 'Base de dados sincronizada com sucesso!' });
  } catch (error: any) {
    console.error('[BRIDGE] Erro no PUSH:', error);
    return NextResponse.json({ error: 'Erro ao gravar banco de dados no servidor' }, { status: 500 });
  }
}
