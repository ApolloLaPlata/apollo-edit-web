import requests
import json
import time

url = "https://macacodriver--apollo-render-router-apollo-api.modal.run/generate/image"

payload = {
    "prompt": "Elon Musk taking an ice cream in a park at night, neon lights in background, high quality photography, cinematic lighting, 8k resolution, highly detailed face",
    "model": "flux2-universal",
    "format": "horizontal",
    "seed": 88888888
}

print("Enviando requisicao Txt2Img do Elon Musk...")
t0 = time.time()
response = requests.post(url, json=payload, stream=True)

if response.status_code == 200:
    for line in response.iter_lines():
        if line:
            data = line.decode('utf-8').strip()
            if not data:
                continue
            
            try:
                res = json.loads(data)
                if "status" in res and res["status"] == "success":
                    import base64
                    with open("testes_modal_output/elon_musk_sorvete_txt2img.png", "wb") as f:
                        f.write(base64.b64decode(res["image_base64"]))
                    print(f"Sucesso! Imagem salva em 'testes_modal_output/elon_musk_sorvete_txt2img.png'")
                    print(f"Tempo total (API): {time.time() - t0:.2f}s")
                    break
                elif "status" in res and res["status"] == "error":
                    print(f"Erro reportado: {res['message']}")
                    break
            except json.JSONDecodeError:
                print(f"Heartbeat Elon (mantendo conexao viva...) - {time.time()-t0:.1f}s decorridos")
else:
    print(f"Erro na conexao: {response.status_code} - {response.text}")
