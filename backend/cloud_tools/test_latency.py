import time
import requests

start = time.time()
print("Iniciando benchmark de latencia Flux 2 Snapshot...")
res = requests.post("https://filosofiadocodigo--apollo-render-router-apollo-api.modal.run/generate/image", json={
    "model": "flux2-universal",
    "prompt": "A cinematic shot of a young man with messy hair and a leather jacket sitting alone at a wooden table in a neon-lit cyberpunk bar, drinking a beer.",
    "format": "square"
})

if res.status_code == 200:
    data = res.json()
    if data.get("status") == "success":
        import base64
        with open("E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\backend\\cloud_tools\\fast_test.png", "wb") as f:
            f.write(base64.b64decode(data["image_base64"]))
        print(f"Sucesso! Imagem salva. Tempo total: {time.time() - start:.2f} segundos!")
        print(f"Render time na nuvem: {data.get('render_time_seconds')} segundos!")
    else:
        print("Erro na geracao:", data)
else:
    print("Erro HTTP:", res.status_code, res.text)
