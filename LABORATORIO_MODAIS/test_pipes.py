import requests
import time

url = "https://historiasde7dias--apollo-render-router-apollo-api.modal.run/generate/audio_lab"

models_to_test = [
    {"model": "sa3", "prompt": "140 bpm, heavy brazilian phonk, distorted 808 bass", "lyrics": "", "duration": 5},
    {"model": "ace-step", "prompt": "brazilian trap, male rapper", "lyrics": "Testando o som", "duration": 10},
]

for payload in models_to_test:
    print(f"Testando {payload['model']}...")
    try:
        t0 = time.time()
        res = requests.post(url, json=payload, timeout=300)
        t1 = time.time()
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                print(f"SUCESSO! Audio recebido em {t1-t0:.1f}s. Tamanho Base64: {len(data.get('audio_base64', ''))}")
            else:
                print(f"ERRO DE LOGICA: {data}")
        else:
            print(f"ERRO HTTP: {res.text}")
    except Exception as e:
        print(f"FALHA NO TESTE: {e}")
    print("-" * 40)
