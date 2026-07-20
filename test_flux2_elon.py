import requests
import json
import base64
import os
import time

url = "https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image"
out_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\testes_modal_output"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "elon_musk_bicicleta_flux2_python.png")

prompt = "A photorealistic cinematic photo of Elon Musk smiling while riding a modern bicycle on a sunny paved street in Silicon Valley, dynamic composition, 8k resolution, ultra detailed portrait consistency"

print(f"[TEST FLUX 2] Enviando requisição para: {url}")
print(f"[TEST FLUX 2] Modelo: flux2-universal (Pure Python na H100)")
print(f"[TEST FLUX 2] Prompt: {prompt}")

t0 = time.time()
response = requests.post(
    url,
    json={
        "model": "flux2-universal",
        "prompt": prompt,
        "format": "horizontal",
        "seed": 12345
    },
    stream=True,
    timeout=600
)

print(f"[TEST FLUX 2] Status HTTP: {response.status_code}")
for line in response.iter_lines():
    if line:
        data = json.loads(line.decode("utf-8"))
        if data.get("type") == "result":
            b64 = data["image_base64"]
            img_bytes = base64.b64decode(b64)
            with open(out_path, "wb") as f:
                f.write(img_bytes)
            elapsed = time.time() - t0
            print(f"✅ SUCESSO! Imagem gerada e salva em: {out_path}")
            print(f"⏱️ Tempo total (incluindo cold start se houve): {elapsed:.2f}s | Tempo de render na H100: {data.get('render_time_seconds')}s")
        elif data.get("type") == "error":
            print(f"❌ ERRO no stream: {data.get('message')}")
