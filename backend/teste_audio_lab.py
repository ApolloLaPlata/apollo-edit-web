import os
import modal

# Força o encoding UTF-8 no Windows para evitar o erro de UnicodeEncodeError do Modal
if os.name == 'nt':
    os.system('chcp 65001')

# Importa o único motor sobrevivente, legalmente seguro para uso comercial
from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine
from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def test_all():
    print("\n--- INICIANDO LABORATÓRIO DE ÁUDIO COMERCIAL-SAFE (STABLE AUDIO OPEN) ---")
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    prompt_sfx = "44k, cinematic, heavy bass, swoosh, impact, metal scrape, high quality"
    prompt_bgm = "44k, instrumental, cyberpunk dark synthwave, slow tempo, deep bass, tense atmosphere"
    
    print("\n[1/2] Testando Stable Audio Open para Efeitos Sonoros (SFX)...")
    stable_audio = StableAudioEngine()
    try:
        wav_sfx = stable_audio.generate_audio.remote(prompt=prompt_sfx, duration_s=5.0, num_inference_steps=200)
        with open("LABORATORIO_MODAIS/testes_audio/stable_audio_sfx.wav", "wb") as f:
            f.write(wav_sfx)
        print("-> Salvo: LABORATORIO_MODAIS/testes_audio/stable_audio_sfx.wav")
    except Exception as e:
        print(f"-> Falha no Stable Audio SFX: {e}")
        
    print("\n[2/2] Testando Stable Audio Open para Música (BGM)...")
    try:
        wav_bgm = stable_audio.generate_audio.remote(prompt=prompt_bgm, duration_s=15.0, num_inference_steps=200)
        with open("LABORATORIO_MODAIS/testes_audio/stable_audio_bgm.wav", "wb") as f:
            f.write(wav_bgm)
        print("-> Salvo: LABORATORIO_MODAIS/testes_audio/stable_audio_bgm.wav")
    except Exception as e:
        print(f"-> Falha no Stable Audio BGM: {e}")

    print("\n--- TESTE FINALIZADO ---")
