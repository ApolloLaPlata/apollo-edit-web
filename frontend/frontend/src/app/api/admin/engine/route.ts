import { NextResponse } from 'next/server';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

let daemonProcess: any = null;

export async function POST(request: Request) {
  const body = await request.json();
  const { action } = body;

  const logFile = path.join(process.cwd(), 'public', 'daemon.log');

  if (action === 'start') {
    if (daemonProcess) {
      return NextResponse.json({ success: false, error: 'Motor já está rodando!' });
    }

    // Limpa o arquivo de log
    fs.writeFileSync(logFile, '[SISTEMA] Iniciando a Frota de Inteligência Artificial...\n');

    // Spawna o daemon usando exec para burlar a análise estática do Next.js
    const { exec } = require('child_process');
    daemonProcess = exec('node daemon.js', { cwd: process.cwd() });

    daemonProcess.stdout.on('data', (data: any) => {
      fs.appendFileSync(logFile, data.toString());
    });

    daemonProcess.stderr.on('data', (data: any) => {
      fs.appendFileSync(logFile, data.toString());
    });

    daemonProcess.on('close', (code: any) => {
      fs.appendFileSync(logFile, `\n[SISTEMA] Motor desligado. Código: ${code}\n`);
      daemonProcess = null;
    });

    return NextResponse.json({ success: true, message: 'Motor iniciado com sucesso.' });
  }

  if (action === 'stop') {
    if (!daemonProcess) {
      return NextResponse.json({ success: false, error: 'Motor já está parado.' });
    }

    daemonProcess.kill();
    daemonProcess = null;
    fs.appendFileSync(logFile, '\n[SISTEMA] Motor desligado manualmente pelo Admin.\n');

    return NextResponse.json({ success: true, message: 'Motor desligado.' });
  }

  if (action === 'status') {
    return NextResponse.json({ 
      success: true, 
      isRunning: daemonProcess !== null 
    });
  }

  return NextResponse.json({ success: false, error: 'Ação inválida.' }, { status: 400 });
}
