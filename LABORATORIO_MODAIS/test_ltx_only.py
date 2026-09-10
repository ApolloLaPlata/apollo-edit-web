import requests
import time

url_video = "https://roxingo--apollo-render-router-api-generate-video.modal.run"
payload = {
    "model": "ltx", 
    "prompt": "A cinematic close up shot of a person speaking in Portuguese, moving their lips naturally, sitting in a dimly lit studio, soft dramatic lighting.",
    "negative_prompt": "worst quality, inconsistent, blurry, deformed, watermark, text",
    "duration": 5
}

print("Iniciando requisição LTX via API...")
start = time.time()
try:
    r = requests.post(url_video, json=payload, stream=True, timeout=600)
except requests.exceptions.Timeout:
    print("Erro: A requisição excedeu o tempo limite de 10 minutos!")
    exit(1)

if r.status_code == 200:
    import base64
    import os
    print("Sucesso! Aguardando stream JSON...")
    data = {}
    import json
    for line in r.iter_lines():
        if line.strip():
            try:
                data = json.loads(line)
                break
            except Exception as e:
                print(f"Ignorando linha não JSON: {line}")
    b64_data = data.get("video_base64", "")
    if not b64_data:
        print("RESPOSTA DA MODAL:", {k: v for k, v in data.items() if k != "video_base64"})
        print("Erro: A API não retornou video_base64! Abortando salvamento do arquivo.")
        exit(1)
        
    out_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_todos_modelos"
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "3_ltx_video_fixed.mp4"), "wb") as f:
        f.write(base64.b64decode(b64_data))
    print(f"Salvo em {time.time() - start:.1f}s")
else:
    print(f"Erro {r.status_code}: {r.text}")
