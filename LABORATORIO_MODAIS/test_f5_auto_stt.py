import base64
import requests
import time

AUDIO_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_tts\rafael_descargas.wav"

with open(AUDIO_PATH, "rb") as f:
    b64_audio = base64.b64encode(f.read()).decode('utf-8')

payload = {
    "text": "Fala galera do Descarga News! Estou testando a transcrição automática no F5.",
    "ref_audio_base64": b64_audio,
    "ref_text": "" # ESTE É O TESTE: Enviando VAZIO!
}

url = "https://neuzamfarias--apollo-api-f5-tts.modal.run"

print(f"Enviando requisicao para {url} (sem texto de ref)...")
t0 = time.time()
r = requests.post(url, json=payload)
print(f"Status: {r.status_code} em {time.time()-t0:.2f}s")

if r.status_code == 200:
    with open("resultado_auto_stt.wav", "wb") as f:
        f.write(r.content)
    print("Salvo em resultado_auto_stt.wav!")
else:
    print(r.text)
