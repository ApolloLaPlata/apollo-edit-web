import requests
import time
import base64
import os
import wave
import struct

def main():
    print("Testando Endpoint API do F5-TTS...")
    
    # Criar um dummy de 5 segundos de silêncio para referência
    dummy_wav_path = "dummy_ref.wav"
    with wave.open(dummy_wav_path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        for i in range(24000 * 5):
            w.writeframes(struct.pack('h', 0))
            
    with open(dummy_wav_path, "rb") as f:
        ref_bytes = f.read()
    ref_b64 = base64.b64encode(ref_bytes).decode("utf-8")
        
    url = "https://apollolaplata--apollo-render-router-api-f5-tts.modal.run"
    
    # 1. Warm-up
    print("Fazendo o Warm-up (carregamento de pesos, vai levar uns minutos para o boot no cold-start)...")
    t0 = time.time()
    try:
        resp = requests.post(url, json={
            "text": "Iniciando sistemas.",
            "ref_audio_base64": ref_b64
        })
        t_warmup = time.time() - t0
        if resp.status_code == 200:
            print(f"Warm-up concluído com sucesso em {t_warmup:.2f}s!")
        else:
            print("Erro no Warmup:", resp.text)
    except Exception as e:
        print("Erro na req do Warmup:", e)
        
    # 2. Teste Real
    texto_teste = "Esta é uma frase de teste longa para medir a velocidade de geração do modelo de português brasileiro no F5 TTS na placa L4 da Modal."
    print(f"Gerando áudio de teste: '{texto_teste}'")
    
    t0 = time.time()
    try:
        resp = requests.post(url, json={
            "text": texto_teste,
            "ref_audio_base64": ref_b64
        })
        t_gen = time.time() - t0
        if resp.status_code == 200:
            print(f"Geração concluída em {t_gen:.2f}s!")
            print(f"Tamanho do arquivo recebido: {len(resp.content)} bytes")
            with open("teste_saida_f5.wav", "wb") as f:
                f.write(resp.content)
        else:
            print("Erro na geração:", resp.text)
    except Exception as e:
        print("Erro na req da geração:", e)
        
    if os.path.exists(dummy_wav_path):
        os.remove(dummy_wav_path)

if __name__ == "__main__":
    main()
