import requests

url = 'http://127.0.0.1:8080/api/lightning_proxy'
payload = {
    'model': 'nvidia-nemotron-3-ultra-550b-a55b',
    'messages': [{'role': 'user', 'content': 'Responda com: Oi, Proxy funcionando!'}]
}

try:
    print('Enviando request para o Proxy...')
    res = requests.post(url, json=payload, timeout=30)
    print(f'Status HTTP: {res.status_code}')
    if res.status_code == 200:
        data = res.json()
        print('Resposta do LLM:', data['choices'][0]['message']['content'])
    else:
        print('Erro no Proxy:', res.text)
except Exception as e:
    print('Excecao no request:', e)
