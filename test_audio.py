import requests
import json
import time

WEBHOOK_URL = 'https://radiodarktrap--apollo-render-router-apollo-api.modal.run/generate/audio_lab'

payload = {
    "prompt": "happy upbeat instrumental children music",
    "engine": "sa3",
    "duration": 5
}

print("Iniciando requisição...")
try:
    with requests.post(WEBHOOK_URL, json=payload, stream=True, timeout=120) as resp:
        for line in resp.iter_lines():
            if line:
                print(line.decode('utf-8'))
except Exception as e:
    print(f"Erro: {e}")
