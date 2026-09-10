import json
import base64
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_krea2_inpaint_modal():
    print('Iniciando teste Krea-2-Raw Inpainting...')
    
    workflow = {
        # 1. Carrega o modelo Krea 2 Raw
        '1': { 'class_type': 'UNETLoader', 'inputs': { 'unet_name': 'Krea-2-Raw.safetensors', 'weight_dtype': 'default' }},
        
        # 2. Carrega os CLIPs (Krea usa os mesmos do Flux/SD3? Vamos tentar o padrao fp16 para SDXL ou T5)
        # Na verdade, a Krea 2 eh um modelo Flux-based ou SD3? A maioria usa CheckpointLoaderSimple. 
        # Vamos testar CheckpointLoaderSimple para garantir que ele acha tudo.
        '2': { 'class_type': 'CheckpointLoaderSimple', 'inputs': { 'ckpt_name': 'Krea-2-Raw.safetensors' }},
        
        # Wait, if Krea 2 Raw is a UNET, we need CLIP. Is it standard? 
        # To be safe, if we use CheckpointLoaderSimple on a pure safetensors it might fail if it's only unet.
        # Let's write the JSON carefully. No, I will use CheckpointLoaderSimple as it handles full checkpoints.
    }

