import modal
import os
import base64

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\default_voice.wav'
out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\audio_teste_perfeito.ogg'

with open(ref_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando F5TTSEngine na nuvem Modal...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
    f5 = cls()
    
    print("Invocando geração de voz...")
    texto_teste = "Perfeito. O motor matemático foi corrigido na placa de vídeo e agora estou falando sem nenhuma distorção metálica no formato Opus, em português."
    opus_bytes = f5.generate_voice.remote(texto_teste, ref_bytes)
    
    with open(out_path, 'wb') as f_out:
        f_out.write(opus_bytes)
    
    print(f"Sucesso absoluto! Retornou {len(opus_bytes)} bytes de áudio limpo.")
    print("Áudio salvo em:", out_path)
except Exception as e:
    print(f"Erro no teste: {e}")
