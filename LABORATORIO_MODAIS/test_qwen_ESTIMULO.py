import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def main():
    print("Iniciando Busca com Texto Estimulante Natural...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
    stt_engine = WhisperTurboSTT()
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text_exact = stt_res.get("text", "")
    
    engine = QwenTtsCloneEngine()
    
    print("\nIniciando geração com Textos Estimulantes (Hahaha, ... e pausas) + Prompt Carregado...")
    
    emocoes = [
        ("Choro_Estimulado", 
         "O ator está em prantos absolutos, sofrendo de depressão profunda. Ele chora compulsivamente enquanto fala. A respiração é ofegante, puxando o ar com dificuldade devido aos soluços dolorosos do choro intenso. A voz dele quebra e falha por causa da tristeza extrema, transmitindo um luto desolador.", 
         "Eu... ahhh... eu não aguento mais... Eles levaram tudo embora. Tudo... tudo que a gente construiu na vida. Meu Deus... não sobrou absolutamente nada..."),
         
        ("Humor_Estimulado", 
         "O ator está em um ataque incontrolável de riso e felicidade. Ele acha a situação incrivelmente hilária e cômica. Ele ri às gargalhadas enquanto fala, num tom de total humor, alegria contagiante e escárnio descontraído, soltando risadas altas e perdendo o fôlego de tanto dar risada da situação.", 
         "Hahahaha! Vocês acham mesmo que eu ia cair nessa? Ai, ai... Hahaha! Foi a coisa mais estúpida que eu já vi na minha vida inteira! Hahahaha!")
    ]
    
    for i, (nome_estado, prompt_direcao, texto_fala) in enumerate(emocoes):
        t_start = time.time()
        print(f"\nProcessando Atuação [{nome_estado}]...")
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
            out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_ESTIMULO_{nome_estado}.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"-> Salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
