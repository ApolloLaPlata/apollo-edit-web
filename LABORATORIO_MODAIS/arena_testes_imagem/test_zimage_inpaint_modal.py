import json
import base64
import os
import rembg
from PIL import Image
import io
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_zimage_inpaint_modal():
    print("Iniciando teste Z-Image Inpainting com rembg...")
    
    img_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/char_ref.png"
    with open(img_path, "rb") as f:
        input_data = f.read()
    
    print("Removendo fundo (criando alpha mask)...")
    output_data = rembg.remove(input_data)
    img_b64 = base64.b64encode(output_data).decode("utf-8")
    
    # Workflow Z-Image Inpainting
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "redzibDX1.safetensors", "weight_dtype": "fp8_e4m3fn" }},
        "2": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_3_4b.safetensors", "type": "lumina2" }},
        "3": { "class_type": "VAELoader", "inputs": { "vae_name": "ae.safetensors" }},
        
        "4": { "class_type": "LoadImage", "inputs": { "image": "referencia_nova_123.png" }},
        "5": { "class_type": "InvertMask", "inputs": { "mask": ["4", 1] }},
        
        "6": { "class_type": "VAEEncodeForInpaint", "inputs": { "pixels": ["4", 0], "mask": ["5", 0], "vae": ["3", 0], "grow_mask_by": 6 }},
        
        "7": { "class_type": "CLIPTextEncode", "inputs": { "text": "a 2d cartoon character running in a futuristic cyberpunk city alley, neon lights, 2d animation style, vibrant colors", "clip": ["2", 0] }},
        "8": { "class_type": "CLIPTextEncode", "inputs": { "text": "bad quality, blurry, deformed, weird anatomy", "clip": ["2", 0] }},
        
        # Z-Image can use KSampler with denoise=1.0 for inpaint
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["7", 0],
            "negative": ["8", 0],
            "latent_image": ["6", 0],
            "seed": 888, "steps": 25, "cfg": 4.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["3", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "zimage_inpaint" }}
    }

    engine = ArenaComfyEngine()
    
    print("Enviando JSON workflow para o servidor Modal Z-Image Inpainting...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="referencia_nova_123.png")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_zimage_inpaint.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)
