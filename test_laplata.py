import requests
import json
import time
import base64

url = "https://apollolaplata--apollo-render-router-apollo-api.modal.run/generate/image"

payload = {
    "prompt": "Portrait of Nicolas Maduro in cyberpunk style, highly detailed",
    "model": "flux2-universal",
    "format": "horizontal",
    "seed": 42
}

print(f"Enviando POST para {url}...")
t0 = time.time()

try:
    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()
    
    print("Conexao estabelecida. Lendo NDJSON...")
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if "status" in data and data["status"] == "success":
                t1 = time.time()
                print(f"SUCESSO! Tempo total: {t1 - t0:.2f}s")
                if "image_base64" in data:
                    b64 = data["image_base64"]
                    # Save image
                    with open("test_laplata_output.png", "wb") as f:
                        f.write(base64.b64decode(b64))
                    print("Imagem salva como test_laplata_output.png")
            else:
                print("UPDATE:", data)
except requests.exceptions.RequestException as e:
    print(f"Erro na requisicao: {e}")
