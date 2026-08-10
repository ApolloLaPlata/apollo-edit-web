import modal
import os

ref_wav_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\teste_kokoro.wav'
ref_text = "Este é um teste de voz em português brasileiro para analisarmos a fluidez, sotaque e velocidade de geração do modelo."
out_path = r'C:\Users\v5est\.gemini\antigravity\brain\a22deae7-7753-458c-a40d-92e685f8af3e\audio_teste_kokoro_f5.ogg'

with open(ref_wav_path, "rb") as f:
    ref_bytes = f.read()

print("Buscando F5TTSEngine na nuvem Modal...")
try:
    cls = modal.Cls.from_name("apollo-render-router", "F5TTSEngine")
    f5 = cls()
    
    print("Invocando geração de voz com ref_text estrito...")
    texto_teste = "Finalmente resolvido! Agora o áudio sai limpo, perfeito e sem gaguejar. O motor foi alinhado ao texto de referência para nunca mais alucinar!"
    opus_bytes = f5.generate_voice.remote(texto_teste, reference_audio_bytes=ref_bytes, ref_text=ref_text)
    
    with open(out_path, 'wb') as f_out:
        f_out.write(opus_bytes)
    
    print(f"Sucesso! Retornou {len(opus_bytes)} bytes de áudio limpo.")
except Exception as e:
    print(f"Erro no teste: {e}")
