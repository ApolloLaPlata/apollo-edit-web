import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import fs from 'fs';
import path from 'path';
import util from 'util';

const execPromise = util.promisify(exec);

// Chave Mestra para acesso remoto do Agente.
const MASTER_KEY = process.env.ANTIGRAVITY_KEY || 'apollo-alpha-omega-2026';

export async function POST(req: Request) {
  try {
    const authHeader = req.headers.get('x-antigravity-key');
    
    if (authHeader !== MASTER_KEY) {
      return NextResponse.json({ success: false, error: 'Acesso Negado. Chave Mestra Inválida.' }, { status: 403 });
    }

    const body = await req.json();
    const { action, payload } = body;

    // AÇÃO 1: EXECUÇÃO DE TERMINAL (SHELL)
    if (action === 'command') {
      try {
        const { stdout, stderr } = await execPromise(payload.command, { cwd: payload.cwd || process.cwd() });
        return NextResponse.json({ success: true, stdout, stderr });
      } catch (cmdError: any) {
        return NextResponse.json({ success: false, stdout: cmdError.stdout, stderr: cmdError.stderr, error: cmdError.message }, { status: 500 });
      }
    }

    // AÇÃO 2: LEITURA DE ARQUIVO
    if (action === 'read_file') {
      const filePath = path.resolve(process.cwd(), payload.path);
      const content = fs.readFileSync(filePath, 'utf-8');
      return NextResponse.json({ success: true, content });
    }

    // AÇÃO 3: ESCRITA DE ARQUIVO
    if (action === 'write_file') {
      const filePath = path.resolve(process.cwd(), payload.path);
      // Garante que o diretório exista
      fs.mkdirSync(path.dirname(filePath), { recursive: true });
      fs.writeFileSync(filePath, payload.content, 'utf-8');
      return NextResponse.json({ success: true, message: 'Arquivo salvo remotamente com sucesso.' });
    }

    return NextResponse.json({ success: false, error: 'Ação desconhecida.' }, { status: 400 });

  } catch (error: any) {
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
