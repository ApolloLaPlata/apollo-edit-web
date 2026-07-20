import modal
import json
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
import base64

from backend.cloud_tools.modal_app import app

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    print("Iniciando teste Universal Engine...")
    
    with open('E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2_universal.json', 'r', encoding='utf-8') as f:
        wf = f.read()
        
    with open(r'C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg', 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode('utf-8')
        
    res = engine.generate.remote(
        workflow_json_string=wf,
        prompt="Jinx do League of Legends sentada num sofa com um gato na perna",
        input_image_b64=img_b64,
        seed=12345
    )
    
    if res.get('status') == 'success':
        out_path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/testes_modal_output/jinx_universal.png'
        with open(out_path, 'wb') as f:
            f.write(base64.b64decode(res['image_base64']))
        print(f"Salvo em {out_path}! Render: {res.get('render_time_seconds')}s")
    else:
        print("ERRO:", res)
