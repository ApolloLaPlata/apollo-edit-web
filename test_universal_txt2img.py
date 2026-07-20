from backend.cloud_tools.modal_app import app
import json
import base64
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    print("Iniciando teste Universal Engine (Text-to-Image)...")
    
    path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/texto_flux2/image_flux2_text_to_image_universal.json'
    with open(path, 'r', encoding='utf-8') as f:
        wf = f.read()
        
    res = engine.generate.remote(
        workflow_json_string=wf,
        prompt="Um homem usando um traje espacial retro futurista fumando um charuto em marte, estilo cinematico, ultra detalhado",
        seed=12345
    )
    
    if res.get('status') == 'success':
        out_path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_modal_output/astronaut_universal.png'
        with open(out_path, 'wb') as f:
            f.write(base64.b64decode(res['image_base64']))
        print(f"Salvo em {out_path}! Render: {res.get('render_time_seconds')}s")
    else:
        print("ERRO:", res)
