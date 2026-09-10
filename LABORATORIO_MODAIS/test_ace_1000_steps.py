import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando teste MAXIMUM OVERDRIVE (1000 Passos) no ACE-Step XL...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    # Adicionada a flag [pt] e os acentos corretos do PT-BR para evitar sotaque de Portugal/Espanhol.
    lyrics = "[pt]\n[Verse]\nBRILHANDO NAS LUZES DA CIDADE\nNÓS ESTAMOS VIVOS\n(Voz ecoando)\n[Chorus]\nE A NOITE NÃO TEM FIM\n[Verse]\nTODO O MUNDO SENTE A ENERGIA\nSUANDO ATÉ O AMANHECER"
    style_tags = "vocal-heavy, lead female singer singing loudly, synth-pop, energetic, bright synths, funky bass, clean modern mix, ultra hi-fi, crystal clear instrumental, pristine studio mastering, 120 bpm"
    
    engine = AceStep15Engine()
    
    steps = 900
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
            out_path = f"LABORATORIO_MODAIS/testes_audio/ace_step_xl_900_passos_ptbr.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            
            print(f"[SUCESSO] Salvo em: {out_path}")
            print(f"Tempo de renderizacao: {res.get('render_time_seconds')}s")
        else:
            print(f"[FALHA] Erro retornado pela engine: {res}")
                
    except Exception as e:
        print(f"Falha critica na execucao com {steps} passos: {e}")

