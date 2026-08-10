import modal
import os

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'
out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\audio_teste_xtts_opus.ogg'

with open(ref_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando XTTS na nuvem Modal...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "XttsEngine")
    xtts = cls()
    
    print("Invocando geração de voz (XTTS + OPUS Ram)...")
    texto_teste = "Perfeito. Retornamos ao modelo X T T S nativo em português. A geração em Opus agora é imediata e sem sotaque gringo."
    opus_bytes = xtts.generate_voice.remote(texto_teste, ref_bytes)
    
    with open(out_path, 'wb') as f_out:
        f_out.write(opus_bytes)
    
    print(f"Sucesso absoluto! Retornou {len(opus_bytes)} bytes de áudio limpo.")
    print("Áudio salvo em:", out_path)
except Exception as e:
    print(f"Erro no teste: {e}")
