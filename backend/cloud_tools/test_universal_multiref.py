import modal
import base64
import json
import time
import sys
import os
sys.path.append(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB")

# O json do Mockup (que tem LoadImage nodes e precisa de Múltiplas Imagens)
WORKFLOW_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\Mockup de Produto(Flux.2 Dev FF8)\image_flux2_fp8.json"

# Duas imagens de teste providas pelo usuário
IMG_1_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX 2 DEV\image_flux2\Captura de tela 2026-06-30 044203.png"
IMG_2_PATH = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX 2 DEV\image_flux2\Captura de tela 2026-06-30 044224.png"

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
import json

def patch_model_names(json_str):
    data = json.loads(json_str)
    lora_nodes = []
    
    # 1. Update model names and find Loras
    for node_id, node in data.items():
        class_type = node.get("class_type", "")
        if class_type == "UNETLoader":
            node["inputs"]["unet_name"] = "flux1-dev.safetensors"
        elif class_type == "VAELoader":
            node["inputs"]["vae_name"] = "ae.safetensors"
        elif class_type == "DualCLIPLoader":
            node["inputs"]["clip_name1"] = "t5xxl_fp16.safetensors"
            node["inputs"]["clip_name2"] = "clip_l.safetensors"
        elif class_type == "LoraLoaderModelOnly":
            lora_nodes.append(node_id)
            
    # 2. Bypass Lora nodes structurally
    for lora_id in lora_nodes:
        lora_node = data[lora_id]
        lora_input_model = lora_node["inputs"].get("model") # e.g. ["12", 0]
        if not lora_input_model:
            continue
            
        # Find all nodes that use this Lora's output and reconnect them to the Lora's input
        for nid, n in data.items():
            if nid == lora_id: continue
            for input_key, input_val in n.get("inputs", {}).items():
                if isinstance(input_val, list) and len(input_val) == 2:
                    if str(input_val[0]) == str(lora_id):
                        # Reconnect
                        n["inputs"][input_key] = lora_input_model
        
        # Delete the bypassed Lora node
        del data[lora_id]
        
    return json.dumps(data)

@app.local_entrypoint()
def run_test():
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        workflow_str = f.read()
        workflow_str = patch_model_names(workflow_str)

    print("[Teste] Workflow lido. Tamanho:", len(workflow_str))

    with open(IMG_1_PATH, "rb") as f1:
        b64_1 = base64.b64encode(f1.read()).decode("utf-8")

    with open(IMG_2_PATH, "rb") as f2:
        b64_2 = base64.b64encode(f2.read()).decode("utf-8")

    print("[Teste] Imagens convertidas para B64. Acionando Motor Universal...")
    t0 = time.time()

    engine = UniversalComfyEngine()
    
    # We pass both images inside 'input_images_b64'
    result = engine.generate.remote(
        workflow_json_string=workflow_str,
        prompt="Apply the design from Reference Image 1 onto objects in Reference Image 2. Make it look futuristic and seamless.",
        input_images_b64=[b64_1, b64_2]
    )

    t1 = time.time()
    
    if result.get("status") == "success":
        print(f"[Teste] SUCESSO! Tempo Total Modal: {t1 - t0:.2f}s")
        print(f"[Teste] Tempo Render Engine: {result.get('render_time_seconds')}s")
        out_b64 = result.get("image_base64")
        out_path = "mockup_result.png"
        with open(out_path, "wb") as out_f:
            out_f.write(base64.b64decode(out_b64))
        print(f"[Teste] Imagem gerada salva em {out_path}")
    else:
        print("[Teste] FALHA!")
        print(result)

if __name__ == "__main__":
    run_test()
