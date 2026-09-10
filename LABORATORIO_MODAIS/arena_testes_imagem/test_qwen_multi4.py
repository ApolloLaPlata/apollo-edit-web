
import json
import base64
import uuid
import os

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_qwen_multi4():
    print("Iniciando teste 4 Personagens com Prompt Blindado no Qwen...")
    
    f1 = f"char1_{uuid.uuid4().hex[:4]}.png"
    f2 = f"char2_{uuid.uuid4().hex[:4]}.png"
    f3 = f"char3_{uuid.uuid4().hex[:4]}.png"
    f4 = f"char4_{uuid.uuid4().hex[:4]}.png"
    
    # Prompt blindado anti-concept-bleeding
    calibrated_prompt = (
        "A dynamic 2d animation style scene in a futuristic cyberpunk city alley with neon lights. "
        "Four distinct characters are standing side-by-side. "
        "Character 1 (image1) is on the far left, blonde hair, clean-shaven, NO BEARD. "
        "Character 2 (image2) is center left, dark hair, has a MUSTACHE ONLY. "
        "Character 3 (image3) is center right, bald with white hair and a thick WHITE BEARD. "
        "Character 4 (image4) is on the far right, dark hair, clean-shaven, NO BEARD. "
        "DO NOT MIX FACIAL FEATURES. Each character MUST strictly maintain their distinct facial hair and features from their respective images. "
        "Vibrant colors, highly detailed."
    )
    
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
        "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
        "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
        
        "5a": { "class_type": "LoadImage", "inputs": { "image": f1 }},
        "5b": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5a", 0] }},
        
        "5c": { "class_type": "LoadImage", "inputs": { "image": f2 }},
        "5d": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5c", 0] }},

        "5e": { "class_type": "LoadImage", "inputs": { "image": f3 }},
        "5f": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5e", 0] }},

        "5g": { "class_type": "LoadImage", "inputs": { "image": f4 }},
        "5h": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5g", 0] }},
        
        "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["3", 0], 
            "prompt": calibrated_prompt, 
            "vae": ["4", 0], 
            "image1": ["5b", 0],
            "image2": ["5d", 0],
            "image3": ["5f", 0],
            "image4": ["5h", 0]
        }},
        "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
        "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1280, "height": 720, "batch_size": 1 }},
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
            "seed": 999, "steps": 25, "cfg": 2.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_multi4" }}
    }

    engine = ArenaComfyEngine()
    
    c1_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char1_turnaround.png"
    c2_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char2_turnaround.png"
    c3_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char3_turnaround.png"
    c4_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char4_turnaround.png"
    
    with open(c1_path, "rb") as f: c1_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(c2_path, "rb") as f: c2_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(c3_path, "rb") as f: c3_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(c4_path, "rb") as f: c4_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    multiple_images = {
        f1: c1_b64,
        f2: c2_b64,
        f3: c3_b64,
        f4: c4_b64
    }
        
    print("Enviando JSON workflow para Modal...")
    
    try:
        result = engine.generate.remote(workflow, multiple_images=multiple_images)
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_qwen_multi4.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor ComfyUI:", result)
            
    except Exception as e:
        print("Erro na execucao da Modal:", e)

