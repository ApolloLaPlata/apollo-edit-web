import os
import requests
import base64

url = "https://apollolaplata--apollo-api-xtts-dev.modal.run"
ref_audio_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\teste_xtts_1786042696.wav"

with open(ref_audio_path, "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode("utf-8")

# O truque mestre: Forçar o XTTS a gerar a Fase 1 usando o texto puramente emocional.
text = "Hahaha! Nossa, isso é maravilhoso! Ahahaha! Eu não acredito que funcionou de primeira!"

payload = {
    "text": text,
    "language": "pt",
    "reference_audio_base64": ref_b64
}

print("Injetando no XTTS para gerar a Matriz da Fase 1...")
response = requests.post(url, json=payload)

if response.status_code == 200:
    save_dir = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "xtts_fase1_mulher_alegria.wav")
    with open(save_path, "wb") as f:
        f.write(response.content)
    print(f"SUCESSO! Matriz XTTS Fase 1 Salva em: {save_path}")
    os.startfile(save_path)
else:
    print(f"Erro no XTTS: {response.text}")
