import modal
import os

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.stable_audio_engine import StableAudioEngine

@app.local_entrypoint()
def main():
    print("Iniciando Bateria de Testes de Efeitos Sonoros (SFX) com Stable Audio Open...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_sfx", exist_ok=True)
    
    sfx_tasks = [
        {
            "name": "Pessoas_Caminhando",
            "prompt": "footsteps on gravel, multiple people walking, ambient sounds, field recording, clear audio",
            "duration": 10
        },
        {
            "name": "Bola_Caindo",
            "prompt": "basketball bouncing and dropping on wooden floor, gym sound, bouncing fading out",
            "duration": 5
        },
        {
            "name": "Carro_Batendo",
            "prompt": "loud car crash, glass breaking, metal crunch, screeching tires, high impact sound effect",
            "duration": 6
        },
        {
            "name": "Tiro",
            "prompt": "gunshot, loud bang, pistol firing, outdoor echo, high quality sound effect",
            "duration": 3
        },
        {
            "name": "Bomba",
            "prompt": "massive explosion, deep rumbling, bomb exploding, cinematic impact, debris falling",
            "duration": 10
        },
        {
            "name": "Fogo",
            "prompt": "crackling fire, campfire burning, embers popping, close up recording, continuous",
            "duration": 15
        }
    ]
    
    engine = StableAudioEngine()
    futures = []
    
    print(f"Enviando {len(sfx_tasks)} tarefas de SFX para a GPU (A10G)...")
    
    for task in sfx_tasks:
        print(f"Agendando {task['name']}...")
        # 100 steps eh o recomendado para Stable Audio
        call = engine.generate_audio.spawn(
            prompt=task["prompt"],
            duration_s=task["duration"],
            num_inference_steps=100
        )
        futures.append({
            "name": task["name"],
            "call": call
        })
            
    print("\nProcessos SFX enfileirados! Aguardando o retorno dos Wavs...")
    
    for item in futures:
        try:
            print(f"Aguardando {item['name']}...")
            wav_bytes = item["call"].get()
            
            out_path = f"LABORATORIO_MODAIS/testes_sfx/{item['name']}.wav"
            with open(out_path, "wb") as f:
                f.write(wav_bytes)
            
            print(f"[SUCESSO] Salvo em: {out_path}")
        except Exception as e:
            print(f"[FALHA] Erro critico em {item['name']}: {e}")

    print("\nBateria SFX concluida!")
