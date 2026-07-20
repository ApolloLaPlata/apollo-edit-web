import time
import requests

start = time.time()
print("Iniciando benchmark de velocidade extrema...")
res = requests.post("https://roxingo--apollo-render-router-api-generate-video.modal.run", json={
    "model": "LTX-2.3-Diffusers",
    "prompt": "A cinematic shot of a racing car driving fast on a wet road at night, reflections, 4k",
    "quality": "fast",
    "duration": 5
})

if res.status_code == 200:
    with open("E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\testes_todos_modelos\\fast_test.mp4", "wb") as f:
        f.write(res.content)
    print(f"Sucesso! Vídeo salvo. Tempo total: {time.time() - start:.2f} segundos!")
else:
    print("Erro:", res.text)
