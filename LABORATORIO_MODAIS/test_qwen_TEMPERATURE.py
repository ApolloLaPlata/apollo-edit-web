import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT

def main():
    print("Iniciando Teste: O Fator Temperatura (Retrocedendo ao Padrão de Tags + Instruct)...")
    
    stt_engine = WhisperTurboSTT()
    engine = QwenTtsCloneEngine()
    
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text = stt_res.get("text", "")
    print(f"Whisper extraiu: '{ref_text}'")
    
    # Retrocedendo para o teste anterior:
    # Apenas o texto limpo com as direções no instruct, 
    # mas usando temperaturas mais altas (0.7 e 1.5).
    # Como as LLMs costumam usar 1.0 como padrão.
    
    texto = "Vocês acham mesmo que eu ia cair nessa? Foi a coisa mais estúpida que eu já vi na minha vida inteira!"
    instruct = "O ator está em um ataque incontrolável de riso e felicidade. Ele ri enquanto fala, num tom de total humor e escárnio descontraído."
    
    temperaturas = [1.2, 1.8]
    
    for t in temperaturas:
        print(f"\nGerando áudio com Temperatura = {t}...")
        t_start = time.time()
        res = engine.clone.remote(
            text=texto,
            ref_audio_b64=b64_ref,
            ref_text=ref_text,
            language="Portuguese",
            instruct=instruct,
            temperature=t
        )
        lat = time.time() - t_start
        print(f"-> Concluído em {lat:.2f}s")
        
        if res.get("audio_base64"):
            out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_TEMP_{str(t).replace('.', '_')}.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(res.get("audio_base64")))
            print(f"-> Salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
