# -*- coding: utf-8 -*-
import urllib.request
import json
import base64
import time
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

text = 'Olá, meu amigo. Esta é uma mensagem de teste para verificar a latência do modelo F5-TTS na Modal. A resposta precisa ser muito rápida.'

with open('default_voice.wav', 'rb') as f:
    ref_b64 = base64.b64encode(f.read()).decode('utf-8')

payload = json.dumps({'text': text, 'ref_audio_base64': ref_b64}).encode('utf-8')
req = urllib.request.Request('https://apollolaplata--apollo-api-f5-tts.modal.run/', method='POST')
req.add_header('Content-Type', 'application/json')

start = time.time()
try:
    with urllib.request.urlopen(req, data=payload) as response:
        audio = response.read()
        end = time.time()
        print(f'Sucesso! Latência: {end - start:.2f} segundos. Bytes recebidos: {len(audio)}')
except Exception as e:
    print(f'Erro: {e}')
