import os
import requests
import base64

url = "https://apollolaplata--apollo-render-router-dev.modal.run"
ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\female_clean_ref.wav"

with open(ref_audio_path, "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode("utf-8")

# O F5-TTS usa tags de emoção direto no texto!
text = "[Laughing] Uau, isso é incrível! Eu não posso acreditar que funcionou tão bem!"

payload = {
    "text": text,
    "ref_audio_base64": ref_b64
}

print("Enviando para F5-TTS...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "f5_mulher_alegria.wav")
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"SUCESSO! Salvo em: {save_path}")
    os.startfile(save_path)
else:
    print(f"Erro: {response.text}")
