import modal
import os
import io
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    import base64
    from backend.cloud_tools.engines.f5_engine import F5TTSEngine
    
    print("Iniciando F5-TTS na Modal...")
    engine = F5TTSEngine()
    
    # Criar um áudio dummy (apenas 1 segundo de silêncio ou ruído)
    import wave
    import struct
    
    dummy_wav_path = "dummy_ref.wav"
    with wave.open(dummy_wav_path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(24000)
        # 1 segundo de mudo
        for i in range(24000):
            w.writeframes(struct.pack('h', 0))
            
    with open(dummy_wav_path, "rb") as f:
        ref_bytes = f.read()
        
    print("Gerando áudio...")
    out_bytes = F5TTSEngine().generate_voice.remote("Isso é um teste do motor F5-TTS rodando em português do Brasil.", ref_bytes)
    print(f"Sucesso! Gerou {len(out_bytes)} bytes de áudio.")
    os.remove(dummy_wav_path)
