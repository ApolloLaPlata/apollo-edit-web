"""
test_pulid_3faces.py
====================
Teste de consistência máxima com PuLID + Flux.1-dev.
Passa as 3 imagens de referência REAIS para o workflow_3_faces_no_masks.json
e gera a cena steampunk com identidade visual travada.
"""

import sys
import os
import json
import base64
import time
import requests
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# ── Configuração ──────────────────────────────────────────────────────────────
MODAL_URL = "https://descarganews--apollo-render-router-apollo-api.modal.run"

# Imagens de referência dos 3 personagens
IMG_JINX       = r"C:\Users\v5est\Downloads\696191561_122139344121114074_799107263541253788_n.jpg"
IMG_ELON       = r"C:\Users\v5est\Downloads\2elon_musk_sorvete_txt2img.png"
IMG_CRYING_MAN = r"C:\Users\v5est\Downloads\Gemini_Generated_Image_trq27dtrq27dtrq2.png"

WORKFLOW_PATH  = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX 2 DEV\image_flux2\workflow_3_faces_no_masks.json"
OUTPUT_PATH    = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\tests\flux_pulid_3faces.jpg"

SCENE_PROMPT = (
    "Cinematic steampunk undercity scene, foggy cobblestone street, "
    "warm gas lamp glow, rusted gears and metallic pipes in background, "
    "three people together: blue-haired girl on the left, "
    "man holding ice cream cone in center, "
    "distressed man in suit holding his head on the right, "
    "photorealistic, 8k, dramatic lighting, atmospheric fog"
)

# ── Helpers ───────────────────────────────────────────────────────────────────
def img_to_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def save_b64_image(b64: str, path: str):
    from PIL import Image
    data = base64.b64decode(b64)
    img = Image.open(io.BytesIO(data))
    img.save(path, quality=95)
    print(f"  [OK] Salvo: {path} ({img.size[0]}x{img.size[1]}px)")

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  TESTE: PuLID 3 Faces — Consistência Máxima")
    print("=" * 60)

    # 1. Carrega workflow
    print("\n[1] Carregando workflow PuLID 3 faces...")
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # 2. Converte imagens de referência para base64
    print("[2] Carregando imagens de referência...")
    b64_jinx  = img_to_b64(IMG_JINX)
    b64_elon  = img_to_b64(IMG_ELON)
    b64_crying = img_to_b64(IMG_CRYING_MAN)
    print(f"  [OK] Jinx:       {len(b64_jinx)//1024} KB")
    print(f"  [OK] Elon:       {len(b64_elon)//1024} KB")
    print(f"  [OK] Crying Man: {len(b64_crying)//1024} KB")

    # 3. Injeta no workflow
    print("[3] Injetando referências e prompt no workflow...")

    # Prompt principal
    for node_id, node in workflow.items():
        if node.get("class_type") == "CLIPTextEncode":
            if "text" in node.get("inputs", {}):
                node["inputs"]["text"] = SCENE_PROMPT

    # Imagens de referência nos nós APOLLO_INPUT_IMAGE_X
    def set_image(node_id, b64_data, filename):
        if node_id in workflow and workflow[node_id].get("class_type") == "LoadImage":
            workflow[node_id]["inputs"]["image"] = filename

    set_image("APOLLO_INPUT_IMAGE_1", b64_jinx,   "ref_jinx.png")
    set_image("APOLLO_INPUT_IMAGE_2", b64_elon,   "ref_elon.png")
    set_image("APOLLO_INPUT_IMAGE_3", b64_crying,  "ref_crying.png")

    # Seed e resolução
    if "98:25" in workflow:
        workflow["98:25"]["inputs"]["noise_seed"] = 42
    if "98:47" in workflow:
        workflow["98:47"]["inputs"]["width"] = 1280
        workflow["98:47"]["inputs"]["height"] = 720

    # Modelos corretos
    for node_id, node in workflow.items():
        inputs = node.get("inputs", {})
        ct = node.get("class_type", "")
        if ct == "UNETLoader":
            inputs["unet_name"] = "flux1-dev.safetensors"
        elif ct == "VAELoader":
            inputs["vae_name"] = "ae.safetensors"
        elif ct == "DualCLIPLoader":
            inputs["clip_name1"] = "t5xxl_fp16.safetensors"
            inputs["clip_name2"] = "clip_l.safetensors"
        elif ct == "PulidFluxModelLoader":
            inputs["pulid_file"] = "pulid_flux_v0.9.1.safetensors"
        elif ct == "StyleModelLoader":
            inputs["style_model_name"] = "flux1-redux-dev.safetensors"
        elif ct == "CLIPVisionLoader":
            inputs["clip_name"] = "sigclip_vision_patch14_384.safetensors"

    # 4. Envia para o endpoint Universal do Modal diretamente via Modal
    print(f"\n[4] Enviando para Modal PuLID engine diretamente via Modal...")
    
    from backend.cloud_tools.modal_app import app
    from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
    
    t0 = time.time()
    
    engine = UniversalComfyEngine()
    
    # Run synchronously in the current app context if we run this file with python
    # We can use a context manager to run the app
    with app.run():
        result = engine.generate.remote(
            workflow_json_string=json.dumps(workflow),
            prompt=SCENE_PROMPT,
            reference_images={
                "ref_jinx.png": b64_jinx,
                "ref_elon.png": b64_elon,
                "ref_crying.png": b64_crying
            }
        )
        
        elapsed = time.time() - t0
        
        if result and result.get("status") == "success" and result.get("image_base64"):
            print(f"\n  🎉 Gerado em {elapsed:.1f}s!")
            save_b64_image(result["image_base64"], OUTPUT_PATH)
        else:
            print(f"\n  [ERROR] Falhou:")
            print(result)

if __name__ == "__main__":
    main()
