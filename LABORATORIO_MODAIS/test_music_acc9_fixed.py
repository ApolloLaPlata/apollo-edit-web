import requests
import json
import os
import time
import base64

URL = 'https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab'
OUTPUT_DIR = 'testes_musica_conta9'
os.makedirs(OUTPUT_DIR, exist_ok=True)

models = ['ace-step', 'sa3', 'minimax']

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
        
        lines = [line for line in resp.text.split('\n') if line.strip()]
        last_json = json.loads(lines[-1])
        
        audio_b64 = last_json.get('audio_base64')
        if audio_b64:
            filename = os.path.join(OUTPUT_DIR, f'teste_{model}.mp3')
            with open(filename, 'wb') as f:
                f.write(base64.b64decode(audio_b64))
            print(f'[{model}] Sucesso em {time.time()-t0:.1f}s. Salvo como {filename}')
        else:
            print(f'[{model}] ERRO: Base64 n?o encontrado no ltimo JSON: {last_json.keys()}')
            
    except Exception as e:
        print(f'[{model}] ERRO: {e}')
