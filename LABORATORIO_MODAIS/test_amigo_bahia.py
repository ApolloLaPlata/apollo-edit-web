import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def main():
    print("Extraindo transcrição Whisper do Áudio do WhatsApp (Amigo Bahia)...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\amigo_bahia_ref.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
    stt_engine = WhisperTurboSTT()
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text_exact = stt_res.get("text", "")
    print(f"Texto detectado do seu amigo (Âncora de 30s): '{ref_text_exact}'\n")
    
    engine = QwenTtsCloneEngine()
    
    texto_fala = "Eu vou ficar muito rico, porque na Bahia é tudo muito fácil, aqui é só água de coco, aqui é Bolsa Família e alegria, trabalho aqui não chega não."
    prompt_direcao = "O ator está muito alegre, rindo de forma descontraída, animada e festiva, falando em tom de deboche bem humorado, com muita energia positiva e dando risadas."
    
    print("Clonando a voz com atuação Alegre...")
    t_start = time.time()
    res = engine.clone.remote(
        text=texto_fala,
        ref_audio_b64=b64_ref,
        ref_text=ref_text_exact,
        language="Portuguese",
        instruct=prompt_direcao
    )
    lat = time.time() - t_start
    print(f"-> Concluído em {lat:.2f}s")
    
    audio_b64 = res.get("audio_base64")
    if audio_b64:
        out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/amigo_bahia_clone.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(audio_b64))
        print(f"-> Salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
