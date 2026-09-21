import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export async function POST(request: Request) {
  try {
    console.log('[API SWARM] Despertando Redação Neural (Robôs Python)...');
    
    // Caminho absoluto para os robôs do backend
    const botsDir = path.resolve(process.cwd(), '..', 'backend_bots');
    const botPath = path.join(botsDir, 'main.py');
    const venvPath = path.join(botsDir, 'venv', 'Scripts', 'python.exe');
    
    // Verifica qual python usar
    const pythonExecutable = fs.existsSync(venvPath) ? `"${venvPath}"` : 'python';
    const command = `${pythonExecutable} "${botPath}"`;
    
    return new Promise<NextResponse>((resolve) => {
      exec(command, { cwd: botsDir }, (error, stdout, stderr) => {
        if (error) {
          console.error(`[API SWARM] Erro de execução: ${error.message}`);
          return resolve(NextResponse.json({ success: false, error: error.message, details: stderr }, { status: 500 }));
        }
        
        console.log(`[API SWARM] Operação Concluída. Log: \n${stdout}`);
        return resolve(NextResponse.json({ success: true, log: stdout }));
      });
    });

  } catch (error: any) {
    console.error('[API SWARM] Falha Crítica:', error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
