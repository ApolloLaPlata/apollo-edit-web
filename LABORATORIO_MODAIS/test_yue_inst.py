import modal
import os
import time
from test_yue_engine import YuEEngine, app

@app.local_entrypoint()
def test_yue_instrumental():
    print("Iniciando laboratório de teste YuE (Instrumental)...")
    os.makedirs("testes_audio", exist_ok=True)
    
    # Técnica oficial do YuE (Issue #18) para Instrumental:
    # Retirar tags vocais do prompt e passar quebras de linha nas letras
    tags = "instrumental, dark trap, hard hitting 808, heavy bass, dark synth, 140 bpm, horrorcore"
    lyrics = "[verse]\n\n\n\n\n[chorus]\n\n\n\n\n[verse]\n\n\n\n\n[chorus]\n\n\n\n\n[outro]\n\n\n"
    
    engine = YuEEngine()
    try:
        start_time = time.time()
        wav_data = engine.generate_song.remote(prompt_tags=tags, lyrics=lyrics)
        end_time = time.time()
        
        timestamp = int(time.time())
        out_path = f"testes_audio/YuE_Inst_Test_{timestamp}.mp3"
        
        with open(out_path, "wb") as f:
            f.write(wav_data)
        print(f"Sucesso! Gerado em {end_time - start_time:.1f}s")
        print(f"Salvo em: LABORATORIO_MODAIS/{out_path}")
    except Exception as e:
        print(f"Falha na inferência YuE: {e}")
