import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def main():
    print("Iniciando Busca Teatral - Extraindo transcrição Whisper...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
    stt_engine = WhisperTurboSTT()
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text_exact = stt_res.get("text", "")
    
    engine = QwenTtsCloneEngine()
    
    print("\nIniciando geração com Textos e Prompts de Teatro Absoluto...")
    
    emocoes = [
        ("Choro_Com_Soluco", 
         "O ator está em prantos, chorando compulsivamente com soluços intensos e dolorosos. Ele puxa o catarro, funga o nariz fortemente, suspira de forma ruidosa e sua voz quebra constantemente. Há o som explícito de choro e lamento de luto ao longo de toda a fala.", 
         "(Fungando forte) Eu... Eu não aguento mais... (Choro) Eles levaram tudo embora! (Soluço) Tudo que a gente construiu na vida... Não sobrou absolutamente nada!"),
         
        ("Odio_Animalesco", 
         "O ator está possuído por uma fúria cega, rosnando, grunhindo e grasnando as palavras como um animal selvagem e raivoso. Ele fala entredentes com ódio profundo, cuspindo as sílabas, e no final solta um grito rasgado, agudo e estridente de pura frustração incontrolável.", 
         "Eu avisei! (Rosnando) Eu falei que essa desgraça ia acontecer! Se aquele infeliz cruzar o meu caminho de novo... (Gritando) EU ACABO COM ELE! ACABO!")
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
            out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_TEATRO_{nome_estado}.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"-> Salvo: {out_path}")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
