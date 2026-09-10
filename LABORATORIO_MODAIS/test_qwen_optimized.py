import modal
import os
import time
import base64

def main():
    try:
        engine_cls = modal.Cls.from_name("apollo-render-router", "QwenTtsCloneEngine")
        engine = engine_cls()
        
        ref_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/dummy_voice.wav"
        if not os.path.exists(ref_path):
            print("Audio de referência não encontrado:", ref_path)
            return
            
        with open(ref_path, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        text = "Esse é um teste de velocidade extrema do modelo Qwen TTS. O objetivo é processar isso na menor latência possível usando BFloat16."
        
        print("--- BENCHMARK OTIMIZADO QWEN TTS ---")
        
        # Iteração de Warm-up
        print("Aquecendo a GPU (Warm-up)...")
        engine.clone.remote(
            text="Warmup",
            ref_audio_b64=ref_b64,
            ref_text="Isso é apenas um teste de voz.",
            language="Portuguese",
            instruct="Normal"
        )
        
        total_time = 0
        iterations = 3
        
        print(f"\nIniciando bateria de emoções com o áudio original...")
        emocoes = [
            ("Agressivo", "Eu não acredito que eles tiveram a coragem de fazer isso de novo!"),
            ("Triste", "Eu não consigo acreditar que nós perdemos tudo aquilo ontem."),
            ("Sussurrando", "Fala bem baixo pra ninguém escutar a gente conversando.")
        ]
        
        for i, (emo, txt) in enumerate(emocoes):
            t_start = time.time()
            res = engine.clone.remote(
                text=txt,
                ref_audio_b64=ref_b64,
                ref_text="Isso é apenas um teste de voz.",
                language="Portuguese",
                instruct=emo
            )
            lat = time.time() - t_start
            print(f"Iteração {i+1} ({emo}): {lat:.2f}s (Render GPU: {res.get('render_time_seconds', 'N/A')}s)")
            
            # Salvar o áudio na pasta correta
            audio_b64 = res.get("audio_base64")
            if audio_b64:
                out_path = f"E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/qwen_bfloat16_emocao_{emo}.wav"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
                print(f"Áudio salvo: {out_path}")

        
    except Exception as e:
        print("Erro Fatal:", str(e))

if __name__ == "__main__":
    main()
