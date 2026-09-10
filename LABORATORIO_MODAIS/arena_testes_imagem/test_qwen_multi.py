
import json
import base64
import uuid
import os

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_qwen_multi_modal():
    print("Iniciando teste Multi-Character com Qwen...")
    
    # Gerar filenames unicos
    f1 = f"char1_{uuid.uuid4().hex[:4]}.png"
    f2 = f"char2_{uuid.uuid4().hex[:4]}.png"
    
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
        "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
        "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
        
        "5a": { "class_type": "LoadImage", "inputs": { "image": f1 }},
        "5b": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5a", 0] }},
        
        "5c": { "class_type": "LoadImage", "inputs": { "image": f2 }},
        "5d": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5c", 0] }},
        
        "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["3", 0], 
            "prompt": "Two characters facing each other. Character 1 (image1) is pointing at Character 2 (image2) in a futuristic cyberpunk city alley, neon lights, 2d animation style.", 
            "vae": ["4", 0], 
            "image1": ["5b", 0],
            "image2": ["5d", 0]
        }},
        "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
        "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }},
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
            "seed": 100, "steps": 20, "cfg": 2.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_multi" }}
    }

    engine = ArenaComfyEngine()
    
    # Ler char1 e char2
    c1_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char1_turnaround.png"
    c2_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char2_turnaround.png"
    
    with open(c1_path, "rb") as f:
        c1_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(c2_path, "rb") as f:
        c2_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    multiple_images = {
        f1: c1_b64,
        f2: c2_b64
    }
        
    print("Enviando JSON workflow para Modal...")
    
    try:
        result = engine.generate.remote(workflow, multiple_images=multiple_images)
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_qwen_multi.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor ComfyUI:", result)
            
    except Exception as e:
        print("Erro na execucao da Modal:", e)

