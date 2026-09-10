import json
import os
import sys
import base64

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_qwen_modal():
    print("Iniciando teste da Arena com ComfyUI...")
    
    # Construindo o Workflow Baseado no Skill qwen-image-edit
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
        "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
        "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
        "5": { "class_type": "LoadImage", "inputs": { "image": "qwen_test_999.png" }},
        "5b": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5", 0] }},
        "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["3", 0], "prompt": "a 2d cartoon character running in a futuristic cyberpunk city alley, neon lights, 2d animation style, vibrant colors", "vae": ["4", 0], "image1": ["5b", 0]
        }},
        "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
        "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1024, "height": 1024, "batch_size": 1 }},
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
            "seed": 42, "steps": 20, "cfg": 2.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_edit_arena" }}
    }

    # Inicializar Engine da Modal
    engine = ArenaComfyEngine()
    print("Lendo imagem de referencia e convertendo para base64...")
    
    img_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char_ref.png"
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    print("Enviando JSON workflow e imagem para o servidor Modal ComfyUI...")
    
    try:
        # A API gerada retornara status e image_b64
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="qwen_test_999.png")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_qwen.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor ComfyUI:", result)
            
    except Exception as e:
        print("Erro na execucao da Modal:", e)


