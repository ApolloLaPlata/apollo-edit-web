import modal
import sys
import os
import time
import base64

def main():
    try:
        engine_cls = modal.Cls.from_name("apollo-render-router", "QwenTtsCloneEngine")
        engine = engine_cls()
        
        # Usando um áudio de referência base já existente na pasta de testes
        ref_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/dummy_voice.wav"
        if not os.path.exists(ref_path):
            print("Audio de referência não encontrado:", ref_path)
            return
            
        with open(ref_path, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        emotions = [
            ("Agressivo", "Fale gritando, com muita raiva e agressividade!"),
            ("Sussurrando", "Fale sussurrando bem baixinho como ASMR, muito calmo."),
            ("Chorando", "Fale chorando e soluçando, com voz triste e embargada."),
            ("Assustado", "Fale gaguejando, com muito medo e pavor na voz.")
        ]
        
        text = "Meu Deus, eu não acredito que nós finalmente conseguimos! A infraestrutura finalmente está online na nova conta."
        
        out_dir = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/resultados_emocionais"
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"Disparando bateria de testes Qwen (Zero-Shot Instruct)...")
        t0 = time.time()
        
        for nome, instruct in emotions:
            print(f"\n[->] Testando emoção: {nome} (Instruct: '{instruct}')")
            t_start = time.time()
            res = engine.clone.remote(
                text=text,
                ref_audio_b64=ref_b64,
                ref_text="Isso é apenas um teste de voz.",
                language="Portuguese",
                instruct=instruct
            )
            lat = time.time() - t_start
            print(f"[<-] Resultado {nome}: {res.get('status')} - Latência total Modal: {lat:.2f}s (Render puro na GPU: {res.get('render_time_seconds', 'N/A')}s)")
            
            if res.get("status") == "success":
                audio_bytes = base64.b64decode(res["audio_base64"])
                with open(os.path.join(out_dir, f"qwen_{nome}.wav"), "wb") as f:
                    f.write(audio_bytes)
            else:
                print("Erro detalhado:", str(res))
        
        print(f"\nTeste de emoções completo em {time.time() - t0:.2f}s!")
        
    except Exception as e:
        print("Erro Fatal:", str(e))

if __name__ == "__main__":
    main()
