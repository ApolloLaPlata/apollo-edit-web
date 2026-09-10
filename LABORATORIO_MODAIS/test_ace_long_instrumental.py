import modal
import os
import base64
from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_15_engine import AceStep15Engine

@app.local_entrypoint()
def main():
    print("Iniciando Teste Massivo: Instrumentais Longos (4 Minutos) no ACE-Step XL...")
    
    os.makedirs("LABORATORIO_MODAIS/testes_audio", exist_ok=True)
    
    # Vamos gerar 4 minutos exatos (240 segundos)
    DURACAO = 240 
    
    # Um prompt forte pra garantir que o modelo saiba que nao deve colocar ninguem cantando
    estilo = "instrumental only, no vocals, no voices, dark commercial trap beat, young thug style, heavy deep 808 bass, crisp fast hi-hats, studio mixing, dynamic structure"
    
    # Lyrics vazios para forçar instrumental
    letra = "" 
    
    tasks = [
        {"nome": "ACE_Instrumental_Longo_700.wav", "steps": 700},
        {"nome": "ACE_Instrumental_Longo_1000.wav", "steps": 1000}
    ]
    
    engine = AceStep15Engine()
    futures = []
    
    print(f"Enviando 2 pedidos colossais de {DURACAO}s para as H100s na nuvem...")
    
    for task in tasks:
        print(f"Agendando {task['nome']} com {task['steps']} passos...")
        call = engine.generate.spawn(
            style_tags=estilo,
            lyrics=letra,
            length_seconds=DURACAO,
            steps=task["steps"]
        )
        futures.append({
            "nome": task["nome"],
            "call": call
        })
        
    print("\nProcessos submetidos! Isso vai exigir muito da GPU. Aguardando retorno...")
    
    for item in futures:
        try:
            print(f"Aguardando conclusao de {item['nome']}...")
            result = item["call"].get()
            
            if result["status"] == "success":
                audio_bytes = base64.b64decode(result["audio_base64"])
                out_path = f"LABORATORIO_MODAIS/testes_audio/{item['nome']}"
                
                with open(out_path, "wb") as f:
                    f.write(audio_bytes)
                
                tempo = result.get('render_time_seconds', '?')
                print(f"[SUCESSO] Salvo em: {out_path} (Tempo de GPU: {tempo}s)")
            else:
                print(f"[FALHA] Erro retornado pela nuvem em {item['nome']}: {result.get('error')}")
                
        except Exception as e:
            print(f"[FALHA CRITICA] Erro local ao processar {item['nome']}: {e}")

    print("\nTeste Massivo Concluido!")
