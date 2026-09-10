import modal
import sys
import os
import time
import base64

def main():
    try:
        engine_cls = modal.Cls.from_name("apollo-render-router", "QwenTtsCloneEngine")
        engine = engine_cls()
        
        # Voz original limpa do Rafael
        ref_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/testes_tts/rafael_descargas_clean.wav"
        if not os.path.exists(ref_path):
            print("Audio de referência não encontrado:", ref_path)
            return
            
        with open(ref_path, "rb") as f:
            ref_b64 = base64.b64encode(f.read()).decode("utf-8")
            
        # O modelo Qwen3-TTS usa ICL (In-Context Learning), e a documentação exige a transcrição correta do áudio base
        ref_text = "Fiz o procedimento duas vezes pra ter certeza. Os pinos estão normais."
        
        # O Mestre exigiu regressão controlada: começar do zero e subir a complexidade
        base_text = "Isso é um teste de clonagem. Vamos ver se a minha voz continua normal e nítida."
        
        emotions = [
            (
                "01_Controle_Zero_Tags",
                "", # Sem nenhuma instrução, apenas o texto base puro que sabemos que funciona.
                base_text
            ),
            (
                "02_Emocao_1_Palavra",
                "Agressivo.",
                "Eu não acredito que eles tiveram a coragem de fazer isso de novo!"
            ),
            (
                "03_Emocao_1_Palavra",
                "Triste.",
                "Eu não consigo acreditar que nós perdemos tudo aquilo ontem."
            ),
            (
                "04_Emocao_1_Palavra",
                "Sussurrando.",
                "Fala bem baixo pra ninguém escutar a gente conversando."
            )
        ]
        
        out_dir = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/resultados_emocionais/rafael_qwen"
        os.makedirs(out_dir, exist_ok=True)
        
        print(f"--- BATERIA DE TESTES DE EMOÇÃO QWEN (VOZ: RAFAEL) ---")
        t0 = time.time()
        
        for nome, instruct, text in emotions:
            print(f"\n[->] Gerando emoção: {nome}")
            print(f"     Instruct: '{instruct}'")
            print(f"     Texto: '{text}'")
            
            t_start = time.time()
            res = engine.clone.remote(
                text=text,
                ref_audio_b64=ref_b64,
                ref_text=ref_text,
                language="Portuguese",
                instruct=instruct
            )
            lat = time.time() - t_start
            
            status = res.get("status")
            if status == "success":
                audio_bytes = base64.b64decode(res["audio_base64"])
                out_file = os.path.join(out_dir, f"rafael_qwen_{nome}.wav")
                with open(out_file, "wb") as f:
                    f.write(audio_bytes)
                print(f"[<-] SUCESSO! Latência: {lat:.2f}s | Salvo em: {out_file}")
            else:
                print(f"[<-] ERRO: {res.get('message')}")
        
        print(f"\nTeste de emoções completo em {time.time() - t0:.2f}s!")
        
    except Exception as e:
        print("Erro Fatal:", str(e))

if __name__ == "__main__":
    main()
