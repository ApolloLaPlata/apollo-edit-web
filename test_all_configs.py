# -*- coding: utf-8 -*-
import json
import random
import os
import subprocess
import asyncio
import modal

print("--- INICIANDO TESTES GERAIS ---")

# 1. TESTE DE ROTEAMENTO DE CHAVES (admin_config.json)
print("\n[1] Testando Roteamento de Chaves Lightning...")
try:
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/admin_config.json', 'r', encoding='utf-8') as f:
        cm = json.load(f)
    keys = cm.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])
    if keys and len(keys) == 4:
        print(f"Sucesso! Encontradas 4 chaves.")
        escolhida = random.choice(keys)
        print(f"Chave aleatória sorteada: {escolhida[:8]}...")
    else:
        print(f"Falha: Chaves não encontradas ou quantidade incorreta. Keys: {keys}")
except Exception as e:
    print(f"Erro no roteamento: {e}")


# 2. TESTE DE CONVERSÃO FFMPEG (WAV -> MP3)
print("\n[2] Testando Conversão FFmpeg em Memória (WAV -> MP3)...")
try:
    import wave
    import struct
    import tempfile
    
    # Criar WAV fictício em memória (1 segundo de silêncio 24kHz Mono 16-bit)
    wav_io = bytearray()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        with wave.open(tmp_wav, 'w') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            for i in range(24000):
                w.writeframes(struct.pack('h', 0))
        tmp_name = tmp_wav.name
        
    with open(tmp_name, 'rb') as f:
        fake_wav_bytes = f.read()
    os.remove(tmp_name)
    
    proc = subprocess.Popen(
        ['ffmpeg', '-i', 'pipe:0', '-f', 'mp3', '-b:a', '64k', 'pipe:1'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
    mp3_bytes, _ = proc.communicate(input=fake_wav_bytes)
    
    if len(mp3_bytes) > 0:
        print(f"Sucesso! Buffer WAV ({len(fake_wav_bytes)} bytes) convertido para MP3 ({len(mp3_bytes)} bytes).")
    else:
        print("Falha na conversão: Retorno vazio do FFmpeg.")
except Exception as e:
    print(f"Erro no FFmpeg: {e}")

print("\n--- TESTES FINALIZADOS ---")
