import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando laboratório TIE-BREAKER (Trap) no ACE-Step XL...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    lyrics = "[pt]\n[Verse]\nNA MADRUGADA O GRAVE BATE FORTE\nOITENTA E OITO NO COMANDO DA SORTE\n[Chorus]\nMEU SOM TE TOCA, A MENTE ENTRA EM CHOQUE\nA RUA SABE QUEM DOMINA O TOPO"
    style_tags = "dark trap, heavy 808 bass, fast rolling hi-hats, gritty, aggressive, male rapper, crisp modern mix, ultra hi-fi, pristine studio mastering, tight low end, 140 bpm"
    
    engine = AceStep15Engine()
    
    for steps in [900, 1000]:
        print(f"\n======================================")
        print(f"Iniciando renderizacao EXTREMA com {steps} passos...")
        try:
            res = engine.generate.remote(
                style_tags=style_tags,
                lyrics=lyrics,
                length_seconds=60,
                steps=steps
            )
            
            if res.get("status") == "success":
                audio_b64 = res["audio_base64"]
                out_path = f"LABORATORIO_MODAIS/testes_audio/ace_step_xl_trap_{steps}_passos_ptbr.wav"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
                
                print(f"[SUCESSO] Salvo em: {out_path}")
                print(f"Tempo de renderizacao: {res.get('render_time_seconds')}s")
            else:
                print(f"[FALHA] Erro retornado pela engine: {res}")
                    
        except Exception as e:
            print(f"Falha critica na execucao com {steps} passos: {e}")

