import base64
import time
import os
import requests
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def main():
    print("Transcrevendo áudio de referência do Rafael para obter o ref_text EXATO...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
    stt_engine = WhisperTurboSTT()
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text_exact = stt_res.get("text", "")
    print(f"Texto de referência exato detectado via Whisper: '{ref_text_exact}'")
    
    engine = QwenTtsCloneEngine()
    
    print("\nIniciando bateria de emoções com a voz do RAFAEL e transcrição exata...")
    emocoes = [
        ("Agressivo", "Eu não acredito que eles tiveram a coragem de fazer isso de novo!"),
        ("Triste", "Eu não consigo acreditar que nós perdemos tudo aquilo ontem."),
        ("Sussurrando", "Fala bem baixo pra ninguém escutar a gente conversando.")
    ]
    
    for i, (emo, txt) in enumerate(emocoes):
        t_start = time.time()
        res = engine.clone.remote(
            text=txt,
            ref_audio_b64=b64_ref,
            ref_text=ref_text_exact,
            language="Portuguese",
            instruct=emo
        )
        lat = time.time() - t_start
        print(f"Iteração {i+1} ({emo}): {lat:.2f}s")
        
        audio_b64 = res.get("audio_base64")
        if audio_b64:
            out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_qwen_FINAL_{emo}.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"Áudio salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
