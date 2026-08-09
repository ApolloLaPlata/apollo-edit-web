import requests
import json
import time

print('Testando /api/lightning_proxy em 8080...')
payload = {
    'model': 'nvidia-nemotron-3-ultra-550b-a55b',
    'messages': [{'role': 'user', 'content': 'Quem Ã© vocÃª e o que vocÃª sabe sobre a arquitetura do Apollo Edit Web? Responda em uma frase.'}]
}

try:
    response = requests.post('http://127.0.0.1:8080/api/lightning_proxy', json=payload, timeout=20)
    print(f'Status: {response.status_code}')
    print('RAW TEXT:', response.text.encode('utf-8').decode('utf-8', 'ignore'))
except Exception as e:
    print('Erro na requisiÃ§Ã£o HTTP:', e)

