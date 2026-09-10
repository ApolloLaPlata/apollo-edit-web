import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine
from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT

def main():
    print("Iniciando Tira-Teima: Sistema de Duas Fases (Clonando a Emoção Sintética)...")
    
    stt_engine = WhisperTurboSTT()
    engine = QwenTtsCloneEngine()
    
    # ---------------------------------------------------------
    # FASE 2 - CHORO
    # Usando o áudio que já está chorando como âncora
    # ---------------------------------------------------------
    print("\n--- Teste 1: FASE 2 (CHORO) ---")
    audio_choro_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_ESTIMULO_Choro_Estimulado.wav"
    with open(audio_choro_path, "rb") as f:
        ref_bytes_choro = f.read()
    b64_ref_choro = base64.b64encode(ref_bytes_choro).decode('utf-8')
    
    stt_res_choro = stt_engine.transcribe.remote(ref_bytes_choro, language="pt")
    ref_text_choro = stt_res_choro.get("text", "")
    print(f"Whisper extraiu da voz sintética (Choro): '{ref_text_choro}'")
    
    texto_novo_choro = "Não dá pra acreditar... Eles me tiraram do grupo... me deixaram completamente sozinho aqui. Meu Deus..."
    instruct_choro = "O ator está em prantos absolutos, sofrendo de depressão profunda. Ele chora compulsivamente enquanto fala. A respiração é ofegante, puxando o ar com dificuldade devido aos soluços dolorosos do choro intenso. A voz dele quebra e falha por causa da tristeza extrema, transmitindo um luto desolador."
    
    print("Gerando áudio Fase 2 (Choro)...")
    t_start = time.time()
    res_choro = engine.clone.remote(
        text=texto_novo_choro,
        ref_audio_b64=b64_ref_choro,
        ref_text=ref_text_choro,
        language="Portuguese",
        instruct=instruct_choro
    )
    lat_choro = time.time() - t_start
    print(f"-> Concluído em {lat_choro:.2f}s")
    
    if res_choro.get("audio_base64"):
        out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_2_FASE_Choro.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(res_choro.get("audio_base64")))
        print(f"-> Salvo: {out_path}")
        
    # ---------------------------------------------------------
    # FASE 2 - HUMOR
    # Usando o áudio que já está rindo como âncora
    # ---------------------------------------------------------
    print("\n--- Teste 2: FASE 2 (HUMOR) ---")
    audio_humor_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_ESTIMULO_Humor_Estimulado.wav"
    with open(audio_humor_path, "rb") as f:
        ref_bytes_humor = f.read()
    b64_ref_humor = base64.b64encode(ref_bytes_humor).decode('utf-8')
    
    stt_res_humor = stt_engine.transcribe.remote(ref_bytes_humor, language="pt")
    ref_text_humor = stt_res_humor.get("text", "")
    print(f"Whisper extraiu da voz sintética (Humor): '{ref_text_humor}'")
    
    texto_novo_humor = "Hahaha! Olha a cara dele, não conseguiu passar nem da primeira fase! Ai, ai... Hahaha! Muito ruim, meu Deus!"
    instruct_humor = "O ator está em um ataque incontrolável de riso e felicidade. Ele acha a situação incrivelmente hilária e cômica. Ele ri às gargalhadas enquanto fala, num tom de total humor, alegria contagiante e escárnio descontraído, soltando risadas altas e perdendo o fôlego de tanto dar risada da situação."
    
    print("Gerando áudio Fase 2 (Humor)...")
    t_start = time.time()
    res_humor = engine.clone.remote(
        text=texto_novo_humor,
        ref_audio_b64=b64_ref_humor,
        ref_text=ref_text_humor,
        language="Portuguese",
        instruct=instruct_humor
    )
    lat_humor = time.time() - t_start
    print(f"-> Concluído em {lat_humor:.2f}s")
    
    if res_humor.get("audio_base64"):
        out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_2_FASE_Humor.wav"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(res_humor.get("audio_base64")))
        print(f"-> Salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
