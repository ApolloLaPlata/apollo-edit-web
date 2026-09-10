import os
import requests
import json
import time

# Puxa a chave da variável de ambiente, ou peça para o usuário colar aqui
API_KEY = os.environ.get("FISH_API_KEY", "COLE_SUA_CHAVE_AQUI")
BASE_URL = "https://api.fish.audio/v1"

if API_KEY == "COLE_SUA_CHAVE_AQUI":
    print("ERRO: Nenhuma chave da Fish Audio encontrada. Exporte FISH_API_KEY ou coloque no arquivo.")
    exit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# 1. Referência da atriz (nossa base neutra)
reference_wav = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\data\audios\mulher_americana.wav"

if not os.path.exists(reference_wav):
    print(f"ERRO: O arquivo de referência {reference_wav} não existe.")
    exit(1)

print("[1/3] Enviando áudio neutro para clonagem (Criando Voice ID)...")
with open(reference_wav, "rb") as f:
    files = {"file": f}
    # Na API real, dependendo da doc, as vezes pedem nome ou outros metadata, mas tentaremos o padrão da comunidade.
    # Nota: Algumas APIs exigem metadata via dict. Vamos tentar o envio direto.
    resp = requests.post(f"{BASE_URL}/voices/clone", headers=headers, files=files)

if resp.status_code != 200:
    print("Erro ao clonar voz:")
    print(resp.text)
    exit(1)

voice_id = resp.json().get("voice_id")
if not voice_id:
    # Se a API retornou diferente, tentaremos o 'id'
    voice_id = resp.json().get("id")

print(f"✅ Voice ID gerado com sucesso: {voice_id}")

# 2. As 3 Matrizes Emocionais Extremas
emocoes = {
    "raiva_anchor": {
        "text": "[furious and screaming with rage] EU NÃO AGUENTO MAIS ISSO!!!",
        "desc": "Raiva Extrema"
    },
    "choro_anchor": {
        "text": "[crying loudly][sobbing uncontrollably] Eu só queria que fosse diferente...",
        "desc": "Choro e Soluço"
    },
    "riso_anchor": {
        "text": "[laughing hysterically] Meu Deus isso é muito engraçado!",
        "desc": "Risada Histérica"
    }
}

pasta_destino = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\resultados_emocionais\fish_s2"
os.makedirs(pasta_destino, exist_ok=True)

print("\n[2/3] Gerando as matrizes emocionais usando o Clone Neutro...")
for nome, config in emocoes.items():
    print(f" -> Gerando: {config['desc']} ({nome})")
    payload = {
        "voice_id": voice_id,
        "text": config["text"],
        # "language": "pt", # Descomente se a API reclamar ou exigir. O Fish reconhece auto pela string.
        "sample_rate": 24000
    }
    
    # Headers para o POST JSON
    json_headers = headers.copy()
    json_headers["Content-Type"] = "application/json"
    
    resp_tts = requests.post(f"{BASE_URL}/tts", json=payload, headers=json_headers)
    
    if resp_tts.status_code == 200:
        caminho_final = os.path.join(pasta_destino, f"{nome}.wav")
        with open(caminho_final, "wb") as f_out:
            f_out.write(resp_tts.content)
        print(f"   ✅ Salvo em: {caminho_final}")
    else:
        print(f"   ❌ Erro ao gerar {nome}: {resp_tts.status_code} - {resp_tts.text}")
    
    time.sleep(2) # Pequena pausa pra não bater em rate limits

print("\n[3/3] Processo concluído! Suas matrizes emocionais (Anchors) estão prontas para o XTTSv2.")
