import requests
import json
import os
import time
import base64

URL = 'https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab'
OUTPUT_DIR = 'testes_musica_conta9'
os.makedirs(OUTPUT_DIR, exist_ok=True)

models = ['acestep', 'sa3', 'minimax']

for model in models:
    print(f'Testando modelo {model}...')
    payload = {
        'prompt': f'A beautiful and cinematic {model} demo track with piano and strings, highly detailed',
        'model': model,
        'duration': 5
    }
    try:
        t0 = time.time()
        resp = requests.post(URL, json=payload, timeout=600)
        resp.raise_for_status()
        
        print(f'[{model}] Status code: {resp.status_code}')
        print(f'[{model}] RAW Output (primeiros 500 chars): {resp.text[:500]}')
        
    except Exception as e:
        print(f'[{model}] ERRO: {e}')
