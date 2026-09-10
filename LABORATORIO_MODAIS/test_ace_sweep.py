import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando laboratório de varredura de passos (ACE-Step XL)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    lyrics = "[Verse]\nBRILHANDO NAS LUZES DA CIDADE\nNOS ESTAMOS VIVOS\n(Voz ecoando)\n[Chorus]\nE A NOITE NAO TEM FIM\n[Verse]\nTODO O MUNDO SENTE A ENERGIA\nSUANDO ATE O AMANHECER"
    style_tags = "vocal-heavy, lead female singer singing loudly, synth-pop, energetic, bright synths, funky bass, clean modern mix, ultra hi-fi, crystal clear instrumental, pristine studio mastering, 120 bpm"
    
    engine = AceStep15Engine()
    
    # Testando 300, 400, 500
    for steps in [300, 400, 500]:
        print(f"\n======================================")
        print(f"Iniciando renderizacao com {steps} passos...")
        try:
            res = engine.generate.remote(
                style_tags=style_tags,
                lyrics=lyrics,
                length_seconds=60,
                steps=steps
            )
            
            if res.get("status") == "success":
                audio_b64 = res["audio_base64"]
                out_path = f"LABORATORIO_MODAIS/testes_audio/ace_step_xl_{steps}_passos.wav"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
                
                print(f"[SUCESSO] Salvo em: {out_path}")
                print(f"Tempo de renderizacao: {res.get('render_time_seconds')}s")
            else:
                print(f"[FALHA] Erro retornado pela engine: {res}")
                    
        except Exception as e:
            print(f"Falha critica na execucao com {steps} passos: {e}")

