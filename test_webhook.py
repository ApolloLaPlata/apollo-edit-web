import requests
import base64
import time

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'

with open(ref_wav_path, "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode('utf-8')

url = "https://apollolaplata--apollo-render-router-apollo-api-xtts.modal.run"

print("Testando POST na nova API Web XTTS...")
try:
    start_time = time.time()
    response = requests.post(url, json={
        "text": "Se este áudio for gerado via requisição POST HTTP, significa que a nossa API web customizada está pronta.",
        "ref_audio_base64": ref_b64
    })
    
    duration = time.time() - start_time
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('content-type')}")
    print(f"Tempo total (HTTP): {duration:.2f}s")
    print(f"Audio recebido: {len(response.content)} bytes")
except Exception as e:
    print(f"Erro: {e}")
