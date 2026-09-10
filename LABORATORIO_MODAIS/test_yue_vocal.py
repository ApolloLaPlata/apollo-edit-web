import modal
import os
import time
from test_yue_engine import YuEEngine, app

@app.local_entrypoint()
def test_yue_vocal_trap():
    print("Iniciando laboratório de teste YuE (Voz + Instrumental Dark Trap)...")
    os.makedirs("testes_audio", exist_ok=True)
    
    tags = "rap, dark trap, hard hitting 808, male aggressive vocals, 140 bpm, horrorcore"
    lyrics = "[Verse]\nSTEPPING IN THE SHADOWS OF MY MIND\nFEEL THE BASS HITTING ON THE SNARE\n[Chorus]\nTHE NIGHT IS OURS, NO LIMITS NOW\n[Verse]\nFEEL THE 808 SHAKING THE GROUND\nAPOLLO EDIT DOMINATING THE BEAT"
    
    engine = YuEEngine()
    try:
        start_time = time.time()
        wav_data = engine.generate_song.remote(prompt_tags=tags, lyrics=lyrics)
        end_time = time.time()
        
        timestamp = int(time.time())
        out_path = f"testes_audio/YuE_Vocal_Trap_{timestamp}.mp3"
        
        with open(out_path, "wb") as f:
            f.write(wav_data)
        print(f"Sucesso! Gerado em {end_time - start_time:.1f}s")
        print(f"Salvo em: {out_path}")
    except Exception as e:
        print(f"Falha na inferência YuE: {e}")
