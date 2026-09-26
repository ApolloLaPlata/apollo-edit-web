'use client';

import React, { useState } from 'react';

/**
 * Fase 98: WebBluetooth Analytics IoT (Experimental)
 * Este componente tenta se conectar a um wearable (ex: smartwatch) via Bluetooth do navegador,
 * para monitorar os batimentos cardíacos do leitor e detectar se a fofoca/artigo causou picos de emoção.
 */

export default function WebBluetoothAnalytics() {
  const [bpm, setBpm] = useState<number | null>(null);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState('');

  const connectHeartRateMonitor = async () => {
    try {
      // @ts-ignore
      if (!navigator.bluetooth) {
        throw new Error('Web Bluetooth API não é suportada por este navegador (Use Chrome/Edge/Opera).');
      }

      // Solicita permissão para parear com qualquer dispositivo que exponha o serviço de Heart Rate (0x180D)
      // @ts-ignore
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ services: ['heart_rate'] }]
      });

      const server = await device.gatt?.connect();
      if (!server) throw new Error('Não foi possível conectar ao servidor GATT do dispositivo.');

      const service = await server.getPrimaryService('heart_rate');
      const characteristic = await service.getCharacteristic('heart_rate_measurement');

      await characteristic.startNotifications();
      setConnected(true);

      characteristic.addEventListener('characteristicvaluechanged', (e: any) => {
        const value = e.target.value;
        // O primeiro byte contém flags de formato, o segundo é o BPM (se formato 8 bits)
        const flags = value.getUint8(0);
        const rate16Bits = flags & 0x1;
        
        let currentBpm = 0;
        if (rate16Bits) {
          currentBpm = value.getUint16(1, /*littleEndian=*/true);
        } else {
          currentBpm = value.getUint8(1);
        }
        
        setBpm(currentBpm);
        
        // Aqui enviaríamos os dados para nossa API `/api/analytics/biometrics` para saber
        // se o parágrafo atual deu um susto no leitor. (Motor Mutante Avançado).
      });

    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="my-8 p-6 bg-slate-900/40 border border-slate-800 rounded-3xl backdrop-blur-xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
        <span className="text-6xl">🫀</span>
      </div>
      <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest mb-2 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
        IoT Bio-Métricas (Experimental)
      </h3>
      <p className="text-slate-400 text-xs mb-4 max-w-sm">
        Conecte seu Smartwatch ou monitor cardíaco para medirmos sua resposta emocional a esta matéria.
      </p>

      {!connected ? (
        <button 
          onClick={connectHeartRateMonitor}
          className="px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 text-xs font-bold rounded-lg transition-colors flex items-center gap-2"
        >
          <span>Bluetooth</span> Pair Device
        </button>
      ) : (
        <div className="flex items-end gap-3 text-red-400">
          <div className="text-4xl font-black">{bpm || '--'}</div>
          <div className="text-xs font-bold mb-1">BPM</div>
        </div>
      )}

      {error && (
        <div className="mt-4 text-xs text-red-500 bg-red-950/40 p-2 rounded-lg border border-red-900/50">
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
