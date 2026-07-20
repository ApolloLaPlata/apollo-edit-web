import requests
import time
import base64
import os

URL = "https://roxingo--apollo-render-router-api-generate-video.modal.run"

prompts = [
    "A realistic brazilian reporter holding a microphone, speaking to the camera in portuguese saying 'Boa noite, estas são as principais notícias do dia'. Urban city background, 4k, hyperrealistic",
    "A brazilian woman sitting at a desk doing a podcast, speaking in portuguese into a studio microphone saying 'Olá a todos, bem vindos a mais um episódio'. Highly detailed, 4k"
]

negative_prompt = "worst quality, inconsistent, blurry, deformed, plastic, doll, 3d render, cg, fake, painting"

print("========================================")
print(" TESTE 1: INÍCIO A FRIO (COLD START)")
print("========================================")
payload_1 = {
    "model": "LTX-2.3-Diffusers",
    "prompt": prompts[0],
    "negative_prompt": negative_prompt,
    "quality": "fast",
    "steps": 25,
    "duration": 5
}

t0 = time.time()
resp1 = requests.post(URL, json=payload_1)
t1 = time.time()

if resp1.status_code == 200:
    data1 = resp1.json().get("data", {})
    warm1 = data1.get("warm_start", False)
    with open("teste_frio.mp4", "wb") as f:
        f.write(base64.b64decode(data1.get("video_base64", "")))
    print(f"✅ VÍDEO 1 GERADO!")
    print(f"⏱️  Tempo Total: {t1 - t0:.2f} segundos")
    print(f"🔥 Warm Start: {warm1}")
else:
    print(f"❌ Erro 1: {resp1.text}")
    exit(1)

print("\n========================================")
print(" TESTE 2: INÍCIO A QUENTE (WARM START)")
print("========================================")
payload_2 = {
    "model": "LTX-2.3-Diffusers",
    "prompt": prompts[1],
    "negative_prompt": negative_prompt,
    "quality": "fast",
    "steps": 25,
    "duration": 5
}

t2 = time.time()
resp2 = requests.post(URL, json=payload_2)
t3 = time.time()

if resp2.status_code == 200:
    data2 = resp2.json().get("data", {})
    warm2 = data2.get("warm_start", False)
    with open("teste_quente.mp4", "wb") as f:
        f.write(base64.b64decode(data2.get("video_base64", "")))
    print(f"✅ VÍDEO 2 GERADO!")
    print(f"⏱️  Tempo Total: {t3 - t2:.2f} segundos")
    print(f"🔥 Warm Start: {warm2}")
else:
    print(f"❌ Erro 2: {resp2.text}")
