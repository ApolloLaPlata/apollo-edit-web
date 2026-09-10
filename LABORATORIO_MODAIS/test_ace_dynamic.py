import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando laboratório de teste ACE-Step na Conta 3 (Descarga News)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    lyrics = "[pt]\n[verse]\n(Voz feminina principal)\nBRILHANDO NAS LUZES DA CIDADE\nNÓS ESTAMOS VIVOS\n(Voz ecoando)\n[chorus]\nE A NOITE NÃO TEM FIM\n[verse]\n(Cantando alto e claro)\nTODO O MUNDO SENTE A ENERGIA\nSUANDO ATÉ O AMANHECER"
    style_tags = "vocal-heavy, lead female singer singing loudly, synth-pop, energetic, bright synths, funky bass, clean modern mix, ultra hi-fi, crystal clear instrumental, pristine studio mastering, 120 bpm"
    
    print("Invocando Modal Pura (Python ACE-Step)...")
    
    engine = AceStep15Engine()
    
    try:
        res = engine.generate.remote(
            style_tags=style_tags,
            lyrics=lyrics,
            length_seconds=60,
            steps=200
        )
        
        if res.get("status") == "success":
            audio_b64 = res["audio_base64"]
            out_path = "LABORATORIO_MODAIS/testes_audio/ace_step_pure_python.wav"
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(audio_b64))
            
            print(f"\n[SUCESSO] Audio gerado e salvo em: {out_path}")
            print(f"Tempo de renderização: {res.get('render_time_seconds')}s")
        else:
            print(f"\n[FALHA] Erro retornado pela engine: {res}")
                
    except Exception as e:
        print(f"Falha critica na execucao: {e}")
