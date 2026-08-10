import modal
import os
import io
import wave
import struct

print("Gerando áudio falso...")
dummy_wav_path = "dummy_ref_opus.wav"
with wave.open(dummy_wav_path, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(24000)
    for i in range(24000):
        w.writeframes(struct.pack('h', 0))

with open(dummy_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando F5TTSEngine na nuvem Modal...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
    f5 = cls()
    
    print("Invocando geração de voz (Teste OPUS Nativo)...")
    opus_bytes = f5.generate_voice.remote("Isso é um teste final para validar a conversão direta em Opus.", ref_bytes)
    
    print(f"Sucesso absoluto! Retornou {len(opus_bytes)} bytes de áudio.")
    
    # Valida formato Opus verificando o header OGG
    if opus_bytes.startswith(b'OggS'):
        print("VERIFICADO: O header do buffer confirma que é um formato OGG/Opus válido.")
    else:
        print("ALERTA: O formato do buffer não parece ser OGG.")
except Exception as e:
    print(f"Erro no teste: {e}")
finally:
    if os.path.exists(dummy_wav_path):
        os.remove(dummy_wav_path)

print("Finalizado.")
