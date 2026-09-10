import requests

url = 'http://163.176.135.59/api/audio/generate'
payload = {
    'prompt': 'Test from Antigravity, 808 bass',
    'engine': 'sa3',
    'duration': 5
}
try:
    print("Enviando request para Oracle...")
    resp = requests.post(url, json=payload, timeout=600)
    print(resp.status_code)
    print(resp.json())
except Exception as e:
    print(f'Erro: {e}')
