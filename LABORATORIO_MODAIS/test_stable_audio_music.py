import modal
import os

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine

@app.local_entrypoint()
def main():
    print("Iniciando Bateria de Testes Musicais (Instrumental) no Stable Audio Open...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_sfx", exist_ok=True)
    
    music_tasks = [
        {
            "name": "Instrumental_Cinematico",
            "prompt": "epic cinematic orchestral score, hans zimmer style, massive brass, soaring strings, thunderous percussion, highly emotional, 4k audio",
            "duration": 47
        },
        {
            "name": "Instrumental_Lofi",
            "prompt": "lo-fi hip hop beat, chillhop, smooth rhodes piano, vinyl crackle, relaxed dusty boom bap drum loop, relaxing background music",
            "duration": 47
        },
        {
            "name": "Instrumental_Trap",
            "prompt": "hard dark trap beat, instrumental no vocals, heavy distorted 808 bass, fast hi-hats, spooky synth melody, 140 bpm, crisp mix",
            "duration": 47
        }
    ]
    
    engine = StableAudioEngine()
    futures = []
    
    print(f"Enviando {len(music_tasks)} beats de 47 segundos (limite maximo) para a A10G...")
    
    for task in music_tasks:
        print(f"Agendando {task['name']}...")
        call = engine.generate_audio.spawn(
            prompt=task["prompt"],
            duration_s=task["duration"],
            num_inference_steps=150  # Um pouco mais de passos para música do que para SFX
        )
        futures.append({
            "name": task["name"],
            "call": call
        })
            
    print("\nProcessos Musicais enfileirados! Aguardando o retorno dos Wavs...")
    
    for item in futures:
        try:
            print(f"Aguardando {item['name']}...")
            wav_bytes = item["call"].get()
            
            out_path = f"LABORATORIO_MODAIS/testes_sfx/StableAudio_{item['name']}.wav"
            with open(out_path, "wb") as f:
                f.write(wav_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path}")
        except Exception as e:
            print(f"[FALHA] Erro critico em {item['name']}: {e}")

    print("\nBateria Musical concluida!")
