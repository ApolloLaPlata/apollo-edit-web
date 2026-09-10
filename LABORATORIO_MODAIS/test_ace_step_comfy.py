import os
import json
import base64
import time

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.ace_step_comfy_engine import AceStepComfyEngine

@app.local_entrypoint()
def run():
    print("Iniciando requisição para ACE-Step no ComfyUI (Modal)...")
    t0 = time.time()
    
    # Carregar o JSON do workflow do usuário
    workflow_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\VERSAO_MASTER_VALIDADA\workflow\WORKFLOW - ACE STEP.json"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_str = f.read()
        
    engine = AceStepComfyEngine()
    
    res = engine.generate.remote(workflow_str)
    
    if res.get("status") == "success":
        audio_b64 = res["audio_base64"]
        audio_data = base64.b64decode(audio_b64)
        
        out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\LABORATORIO_MODAIS\testes_audio\ace_step_comfy_test.wav"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        with open(out_path, "wb") as f:
            f.write(audio_data)
            
        print(f"Sucesso! Audio salvo em: {out_path}")
        print(f"Tempo de renderização (nuvem): {res.get('render_time_seconds')}s")
        print(f"Tempo total (local): {time.time() - t0:.1f}s")
    else:
        print(f"Erro na geração: {res.get('message')}")

if __name__ == "__main__":
    run()
