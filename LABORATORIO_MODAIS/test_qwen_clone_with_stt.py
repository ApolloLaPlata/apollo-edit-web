import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT

def test_clone_proper():
    print("Transcrevendo áudio de referência para obter o ref_text EXATO...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    import requests
    
    print("Chamando endpoint do Whisper STT na nuvem...")
    try:
        req = requests.post(
            "https://apollolaplata--apollo-api-transcribe-dev.modal.run", 
            files={"file": ("audio.wav", ref_bytes, "audio/wav")}
        )
        stt_res = req.json()
    except Exception as e:
        print("Erro de conexao no STT:", e)
        return
    
    if "error" in stt_res:
        print("Erro no STT:", stt_res["error"])
        return
        
    ref_text_exact = stt_res.get("text", "")
    print(f"Texto de referência exato detectado: '{ref_text_exact}'")
    
    print("Enviando para clonagem...")
    engine = QwenTtsCloneEngine()
    
    # Texto a sintetizar
    texto = "Agora sim, mestre! Quando a gente passa o texto de referência exato, a clonagem se alinha perfeitamente e o português sai cristalino!"
    
    res = engine.clone.remote(
        text=texto,
        ref_audio_b64=b64_ref,
        ref_text=ref_text_exact, # AQUI ESTAVA O ERRO ANTES!
        language="Portuguese"
    )
    
    if res["status"] == "success":
        out_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_qwen_clone2.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(res["audio_base64"]))
        print(f"Sucesso! Salvo em {out_path}")
    else:
        print("Erro:", res)

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        test_clone_proper()
