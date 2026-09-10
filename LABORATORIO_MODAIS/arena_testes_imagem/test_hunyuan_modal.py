import json
import os
import sys
import base64

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_hunyuan_modal():
    print("Iniciando teste da Arena com ComfyUI (Hunyuan 3.0)...")
    
    # Workflow Hunyuan 3.0 extraido da arquitetura MCP/Flux2Comfy
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "hunyuan_video_3.0_fp8.safetensors", "weight_dtype": "fp8_e4m3fn" }},
        "2": { "class_type": "DualCLIPLoader", "inputs": { "clip_name1": "clip_l.safetensors", "clip_name2": "llava_llama3_fp8_scaled.safetensors", "type": "hunyuan_video" }},
        "3": { "class_type": "VAELoader", "inputs": { "vae_name": "hunyuan_vae.safetensors" }},
        "4": { "class_type": "EmptyHunyuanLatentVideo", "inputs": { "width": 848, "height": 480, "length": 1, "batch_size": 1 }},
        "5": { "class_type": "CLIPTextEncode", "inputs": { "text": "a cinematic photo of a muscular man wearing a black beanie and punisher tank top, riding a mountain bike on a sunny beach boardwalk", "clip": ["2", 0] }},
        "6": { "class_type": "CLIPTextEncode", "inputs": { "text": "", "clip": ["2", 0] }},
        "7": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["4", 0],
            "seed": 42, "steps": 20, "cfg": 3.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "8": { "class_type": "VAEDecode", "inputs": { "samples": ["7", 0], "vae": ["3", 0] }},
        "9": { "class_type": "SaveImage", "inputs": { "images": ["8", 0], "filename_prefix": "hunyuan_arena" }}
    }

    engine = ArenaComfyEngine()
    print("Enviando JSON workflow para o servidor Modal ComfyUI...")
    
    try:
        result = engine.generate.remote(workflow)
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_hunyuan.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor ComfyUI:", result)
            
    except Exception as e:
        print("Erro na execucao da Modal:", e)
