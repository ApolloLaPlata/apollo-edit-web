import requests
import base64
import time
import sys

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'

with open(ref_wav_path, "rb") as f:
    ref_b64 = base64.b64encode(f.read()).decode('utf-8')

# A URL do nosso novo Web Endpoint (verificado no log de deploy)
url = "https://apollolaplata--apollo-api-xtts.modal.run"

texto_longo = (
    "O Sistema Apollo Edit Web agora opera com inteligência artificial avançada. "
    "Diferente dos sistemas convencionais que dependem de locutores humanos, "
    "nós integramos uma nuvem de processamento massivo utilizando placas de vídeo L4. "
    "Isso nos permite não só ler notícias curtas, mas também processar dossiês longos e "
    "complexos em questão de segundos. A voz é sintetizada em formato Opus para garantir "
    "que o usuário final não sofra com travamentos ou lentidão durante o carregamento da página. "
    "E o mais impressionante: o sistema é capaz de reproduzir o sotaque brasileiro com extrema naturalidade, "
    "eliminando aquele tom robótico característico de motores de voz antigos."
)

print(f"Enviando requisição POST para o Web Endpoint...\nTamanho do texto: {len(texto_longo)} caracteres.\n")

try:
    start_time = time.time()
    response = requests.post(url, json={
        "text": texto_longo,
        "ref_audio_base64": ref_b64
    })
    duration = time.time() - start_time
    
    if response.status_code == 200:
        # Salvar o áudio recebido
        out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\audio_teste_longo_xtts.ogg'
        with open(out_path, 'wb') as f:
            f.write(response.content)
            
        print(f"SUCESSO!")
        print(f"Status Code: {response.status_code}")
        print(f"Tempo total (HTTP + Inferencia L4 + FFmpeg Opus): {duration:.2f} segundos")
        print(f"Tamanho do Audio Gerado (Opus): {len(response.content) / 1024:.2f} KB")
        print(f"Audio salvo em: {out_path}")
    else:
        print(f"Erro da API! Code: {response.status_code}\nMessage: {response.text}")
        
except Exception as e:
    print(f"Erro catastrófico: {e}")
