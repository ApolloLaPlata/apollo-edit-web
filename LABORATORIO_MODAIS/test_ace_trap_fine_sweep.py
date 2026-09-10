import modal
import os
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando bateria FINA de TRAP COMERCIAL (O Teste do Vera Definitivo)...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    tags = "brazilian portuguese, commercial melodic trap, young thug style, clean autotune vocals, tight crisp 808 bass, clear pronunciation, radio hit, high fidelity modern mix, 140 bpm"
    lyrics = "[pt-BR]\n[Verse]\nNO MEU COPO TEM GELO, NA MENTE TEM OURO\nEU VIM DO NADA, HOJE EU SOU O TESOURO\n[Chorus]\nPASSO DE NAVE NA RUA, ELA OLHA PRA MIM\nSABE QUE A VIDA É UM FILME, NÃO TEM UM FIM"
    
    # Varredura granular: de 700 a 1000 de 50 em 50.
    steps_list = [700, 750, 800, 850, 900, 950, 1000]
    
    engine = AceStep15Engine()
    futures = []
    
    print(f"Enviando {len(steps_list)} processos paralelos pra H100...")
    
    for step in steps_list:
        print(f"Agendando TRAP Comercial com {step} passos...")
        call = engine.generate.spawn(
            style_tags=tags,
            lyrics=lyrics,
            length_seconds=60,
            steps=step
        )
        futures.append({
            "step": step,
            "call": call
        })
            
    print("\nJobs enfileirados! Aguardando o retorno da varredura...")
    
    for item in futures:
        try:
            print(f"Aguardando resultado de {item['step']}...")
            res = item["call"].get()
            
            if res.get("status") == "success":
                audio_b64 = res["audio_base64"]
                out_path = f"LABORATORIO_MODAIS/testes_audio/ace_trap_comercial_{item['step']}.wav"
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
                
                print(f"[SUCESSO] Salvo em: {out_path} ({res.get('render_time_seconds')}s)")
            else:
                print(f"[FALHA] Erro em {item['step']}: {res}")
        except Exception as e:
            print(f"Falha critica em {item['step']}: {e}")

    print("\nTeste de micro-detalhe concluido!")
