import json
import os
import sys
import base64

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_zimage_modal():
    print("Iniciando teste da Arena com ComfyUI (Z-Image)...")
    
    # Workflow Z-Image extraido do MCP
    workflow = {
        "3": {"inputs": {"seed": 42, "steps": 10, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0, "model": ["16", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["13", 0]}, "class_type": "KSampler"},
        "6": {"inputs": {"text": "a cinematic photo of a muscular man wearing a black beanie and punisher tank top, riding a mountain bike on a sunny beach boardwalk", "clip": ["18", 0]}, "class_type": "CLIPTextEncode"},
        "7": {"inputs": {"text": "blurry ugly bad", "clip": ["18", 0]}, "class_type": "CLIPTextEncode"},
        "8": {"inputs": {"samples": ["3", 0], "vae": ["17", 0]}, "class_type": "VAEDecode"},
        "9": {"inputs": {"filename_prefix": "zimage_arena", "images": ["8", 0]}, "class_type": "SaveImage"},
        "13": {"inputs": {"width": 1024, "height": 1024, "batch_size": 1}, "class_type": "EmptySD3LatentImage"},
        "16": {"inputs": {"unet_name": "redzibDX1.safetensors", "weight_dtype": "default"}, "class_type": "UNETLoader"},
        "17": {"inputs": {"vae_name": "ae.safetensors"}, "class_type": "VAELoader"},
        "18": {"inputs": {"clip_name": "qwen_3_4b.safetensors", "type": "lumina2", "device": "default"}, "class_type": "CLIPLoader"}
    }

    engine = ArenaComfyEngine()
    print("Enviando JSON workflow para o servidor Modal ComfyUI...")
    
    try:
        result = engine.generate.remote(workflow)
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_zimage.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor ComfyUI:", result)
            
    except Exception as e:
        print("Erro na execucao da Modal:", e)
