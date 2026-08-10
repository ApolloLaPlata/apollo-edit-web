import modal
import time

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'

with open(ref_wav_path, "rb") as f:
    ref_bytes = f.read()

try:
    cls = modal.Cls.from_name("apollo-render-router", "XttsEngine")
    xtts = cls()
    
    texto_teste = "Testando a velocidade de inferencia na GPU L4. Sera que o tempo caiu de 9 segundos para menos de 4 segundos? Vamos descobrir agora."
    
    start_time = time.time()
    opus_bytes = xtts.generate_voice.remote(texto_teste, ref_bytes)
    end_time = time.time()
    
    duration = end_time - start_time
    
    print(f"SUCESSO!")
    print(f"Tempo total de resposta (Rede + Inferencia): {duration:.2f} segundos")
    print(f"Tamanho do Audio (Opus): {len(opus_bytes)} bytes")
except Exception as e:
    print(f"Erro no teste: {e}")
