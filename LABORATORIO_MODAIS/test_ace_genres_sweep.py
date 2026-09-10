import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando bateria maciça de testes: 3 Gêneros x 4 Steps (700, 800, 900, 1000)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    tasks = [
        {
            "name": "Voz_Violao",
            "tags": "brazilian portuguese, acoustic guitar, intimate male vocal, clean, high fidelity, 85 bpm, mpb, pristine acoustic",
            "lyrics": "[pt-BR]\n[Verse]\nSÓ VOCÊ E EU NA BEIRA DO MAR\nVIOLÃO TOCANDO ATÉ O SOL RAIAR\n[Chorus]\nESSA NOITE É NOSSA, DEIXA ACONTECER\nTUDO QUE EU QUERIA ERA SÓ VOCÊ"
        },
        {
            "name": "Rock",
            "tags": "brazilian portuguese, hard rock, electric guitar overdrive, punchy drums, aggressive male vocal, clean mix, high fidelity, 130 bpm",
            "lyrics": "[pt-BR]\n[Verse]\nNA CONTRAMÃO DESSA CIDADE LOUCA\nAUMENTA O VOLUME QUE A VIDA É POUCA\n[Chorus]\nACELERA O CARRO, RASGANDO O VENTO\nROCK AND ROLL É O NOSSO SENTIMENTO"
        },
        {
            "name": "Trap",
            "tags": "brazilian portuguese, clean trap, tight punchy 808 bass, crisp hi-hats, clear male rap vocals, high fidelity, clear mix, 140 bpm",
            "lyrics": "[pt-BR]\n[Verse]\nSUBINDO O MORRO DE NAVE DO ANO\nFOCADO NO PLUG, CONTANDO MEUS PLANO\n[Chorus]\nGRAVE BATENDO NO SOM DA FAVELA\nO TOPO É NOSSO, EU FIZ ISSO PRA ELA"
        }
    ]
    
    steps_list = [700, 800, 900, 1000]
    
    engine = AceStep15Engine()
    
    # Vamos enviar as chamadas assincronamente (spawn) para acelerar e usar múltiplas GPUs
    futures = []
    print("Enviando 12 jobs para a nuvem da Modal...")
    
    for task in tasks:
        for step in steps_list:
            print(f"Agendando {task['name']} - {step} passos...")
            call = engine.generate.spawn(
                style_tags=task["tags"],
                lyrics=task["lyrics"],
                length_seconds=60,
                steps=step
            )
            futures.append({
                "name": task["name"],
                "step": step,
                "call": call
            })
            
    print("\nTodos os jobs enfileirados! Aguardando resultados (isso pode levar alguns minutos)...")
    
    for item in futures:
        try:
            print(f"Aguardando resultado de {item['name']} - {item['step']}...")
            res = item["call"].get() # Bloqueia ate finalizar
            
            if res.get("status") == "success":
                audio_b64 = res["audio_base64"]
                out_path = f"LABORATORIO_MODAIS/testes_audio/ace_{item['name']}_{item['step']}_passos.wav"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
                
                print(f"[SUCESSO] Salvo em: {out_path} ({res.get('render_time_seconds')}s)")
            else:
                print(f"[FALHA] Erro em {item['name']} {item['step']}: {res}")
        except Exception as e:
            print(f"Falha critica em {item['name']} {item['step']}: {e}")

    print("\nTodos os testes concluidos!")
