import requests

base_key = '16338b74-3f36-4c89-84db-a8e00b099058'
formats = [
    base_key,
    f"{base_key}/roxingo-org",
    f"{base_key}/roxingo"
]

payload = {
    'model': 'nvidia-nemotron-3-ultra-550b-a55b',
    'messages': [{'role': 'user', 'content': 'Oi'}],
    'max_tokens': 10
}

for key in formats:
    print(f"Testando formato: {key}")
    headers = {
        'Authorization': f"Bearer {key}",
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post('https://lightning.ai/api/v1/chat/completions', json=payload, headers=headers, timeout=10)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print("SUCESSO!")
            break
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro na req: {e}")
    print("-" * 20)
