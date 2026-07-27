import urllib.request
import json
import time

print('Bate direto no localhost:8000 de dentro da Oracle VPS')
req = urllib.request.Request('http://127.0.0.1:8000/api/studio/modal/generate_image', 
    data=json.dumps({
        'prompt': 'A 8k resolution photo of a cyberpunk city',
        'model': 'flux2-universal',
        'format': 'horizontal',
        'steps': 20
    }).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
start = time.time()
try:
    resp = urllib.request.urlopen(req, timeout=300)
    data = json.loads(resp.read().decode('utf-8'))
    print('Status: 200 OK')
    print(f'Tempo total (Oracle -> Modal -> Oracle): {time.time() - start:.2f}s')
    if data.get('status') == 'success':
        print('SUCESSO ABSOLUTO! Imagem base64 recebida de volta com sucesso.')
    else:
        print('ERRO no payload:', data)
except Exception as e:
    print('Erro:', e)
