import requests
import time
import os
import base64

url_video = "https://roxingo--apollo-render-router-api-generate-video.modal.run"
payload = {
    "model": "wan", 
    "prompt": "A camera slowly orbiting a rapper performing on a rooftop at night, neon city behind.",
    "negative_prompt": "text, subtitles, logos, washed out, low quality, flicker, deformed faces",
    "duration": 5,
    "quality": "hd", # Mapeia para 480p no código
    "aspect_ratio": "horizontal"
}

print("Iniciando requisição WAN2.1 via API...")
start = time.time()
try:
    r = requests.post(url_video, json=payload, stream=True, timeout=1200) # 20 minutos
except requests.exceptions.Timeout:
    print("Erro: A requisição excedeu o tempo limite!")
    exit(1)

if r.status_code == 200:
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
    with open(os.path.join(out_dir, "4_wan_video.mp4"), "wb") as f:
        f.write(base64.b64decode(b64_data))
    print(f"Salvo em {time.time() - start:.1f}s no diretório: {out_dir}")
else:
    print(f"Erro: {r.status_code}")
    print(r.text)
