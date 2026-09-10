import base64
import time
from backend.cloud_tools.engines.qwen_tts_clone_engine import QwenTtsCloneEngine

def main():
    print("Iniciando Busca pela ALMA DO RAFAEL - Extraindo transcrição Whisper...")
    audio_path = "E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\LABORATORIO_MODAIS\\testes_tts\\rafael_descargas_clean.wav"
    with open(audio_path, "rb") as f:
        ref_bytes = f.read()
    b64_ref = base64.b64encode(ref_bytes).decode('utf-8')
    
    # 1. Obter texto exato usando WhisperTurboSTT via RPC nativo
    from backend.cloud_tools.engines.stt_engine import WhisperTurboSTT
    stt_engine = WhisperTurboSTT()
    stt_res = stt_engine.transcribe.remote(ref_bytes, language="pt")
    ref_text_exact = stt_res.get("text", "")
    print(f"Texto âncora perfeito: '{ref_text_exact}'\n")
    
    engine = QwenTtsCloneEngine()
    
    print("Iniciando geração com Direções de Palco (Acting Prompts) Extremos...")
    
    emocoes = [
        ("Furia_Absoluta", 
         "O ator está fora de si, gritando com ódio gutural, respiração ofegante e perdendo o controle vocal de tanta fúria. Ele está em um acesso de raiva extrema e fala muito alto.", 
         "Eu não acredito que eles tiveram a coragem de fazer isso de novo! É inaceitável!"),
         
        ("Desespero_Profundo", 
         "O ator está devastado, com a voz embargada de choro. Ele faz pausas longas, chorando, respirando com dificuldade e engolindo o seco, quase sussurrando de tanta dor e desespero.", 
         "Eu não consigo acreditar que nós perdemos tudo aquilo ontem... Tudo."),
         
        ("Deboche_Sarcastico", 
         "O ator está sorrindo ironicamente, rindo de forma debochada e sarcástica. O tom de voz é de total superioridade e desdém, soltando risadinhas enquanto fala.", 
         "Nossa, que surpresa! Eu jamais poderia imaginar que vocês iam fazer essa burrada gigantesca! Hahaha!"),
         
        ("Medo_Sussurrado", 
         "O ator está apavorado, ofegante, e fala sussurrando bem baixinho para não ser ouvido. A voz treme de medo intenso e pânico.", 
         "Fala bem baixo pra ninguém escutar a gente conversando... Eles estão logo ali fora.")
    ]
    
    for i, (nome_estado, prompt_direcao, texto_fala) in enumerate(emocoes):
        t_start = time.time()
        print(f"Processando [{nome_estado}]...")
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
            out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_ALMA_{nome_estado}.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            print(f"-> Salvo: {out_path}\n")

if __name__ == "__main__":
    from backend.cloud_tools.modal_app import app
    with app.run():
        main()
