import modal
import os
import time

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'

with open(ref_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando XTTS na nuvem Modal (Testando Velocidade na L4 + Snapshot)...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "XttsEngine")
    xtts = cls()
    
    texto_teste = "Testando a velocidade de inferência na GPU L4. Será que o tempo caiu de 9 segundos para menos de 4 segundos? Vamos descobrir agora."
    
    print(f"Texto: '{texto_teste}'")
    print("Enviando requisição (Cronometrando...)")
    
    start_time = time.time()
    opus_bytes = xtts.generate_voice.remote(texto_teste, ref_bytes)
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"✅ SUCESSO!")
    print(f"⏱️ Tempo total de resposta (Rede + Inferência): {duration:.2f} segundos")
    print(f"📦 Tamanho do Áudio (Opus): {len(opus_bytes)} bytes")
except Exception as e:
    print(f"Erro no teste: {e}")
