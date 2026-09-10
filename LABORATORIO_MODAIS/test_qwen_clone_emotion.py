import base64
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
import requests

def test_clone_emotion():
    print("Transcrevendo áudio de referência para obter o ref_text EXATO...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    req = requests.post(
        "https://apollolaplata--apollo-api-transcribe-dev.modal.run", 
        files={"file": ("audio.wav", ref_bytes, "audio/wav")}
    )
    stt_res = req.json()
    ref_text_exact = stt_res.get("text", "")
    print(f"Texto de referência exato detectado: '{ref_text_exact}'")
    
    print("Enviando para clonagem com INSTRUCT de raiva...")
    engine = QwenTtsCloneEngine()
    
    # Texto a sintetizar
    texto = "Puta que pariu, eu não aguento mais esse sistema travando toda hora! Que ódio absurdo!"
    
    res = engine.clone.remote(
        text=texto,
        ref_audio_b64=b64_ref,
        ref_text=ref_text_exact,
        language="Portuguese",
        instruct="O personagem está com muita raiva, gritando furioso."
    )
    
    if res["status"] == "success":
        out_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_qwen_clone_raiva.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(res["audio_base64"]))
        print(f"Sucesso! Salvo em {out_path}")
    else:
        print("Erro:", res)

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        test_clone_emotion()
