import json
import base64
import os
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def run_zimage_real_img2img():
    print("Iniciando teste Z-Image REAL Img2Img...")
    
    # Workflow Z-Image Img2Img focado em refinar imagem com multiplos personagens
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "redzibDX1.safetensors", "weight_dtype": "fp8_e4m3fn" }},
        "2": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_3_4b.safetensors", "type": "lumina2" }},
        "3": { "class_type": "VAELoader", "inputs": { "vae_name": "ae.safetensors" }},
        
        "4": { "class_type": "LoadImage", "inputs": { "image": "referencia_multi.jpg" }},
        "5": { "class_type": "VAEEncode", "inputs": { "pixels": ["4", 0], "vae": ["3", 0] }},
        
        "6": { "class_type": "CLIPTextEncode", "inputs": { "text": "A cinematic high quality masterpiece photo of three characters sitting at a rustic bar. On the left, Jinx from Arcane with blue hair and tattoos drinking a blue cocktail. In the middle, a middle-aged man with glasses, mustache, and pink shirt holding a glass of whiskey. On the right, a chimpanzee wearing a flat cap and brown cardigan holding a glass of whiskey. Warm atmospheric lighting, extreme detail, photorealistic.", "clip": ["2", 0] }},
        "7": { "class_type": "CLIPTextEncode", "inputs": { "text": "bad quality, blurry, deformed, cartoon, ugly, missing limbs, watermark", "clip": ["2", 0] }},
        
        # Sampler (Denoise 0.4 para refinar e manter a consistência original)
        "8": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
            "seed": 1024, "steps": 30, "cfg": 4.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.45
        }},
        
        "9": { "class_type": "VAEDecode", "inputs": { "samples": ["8", 0], "vae": ["3", 0] }},
        "10": { "class_type": "SaveImage", "inputs": { "images": ["9", 0], "filename_prefix": "zimage_multi_img2img" }}
    }

    engine = ArenaComfyEngine()
    
    img_path = "C:/Users/v5est/.gemini/antigravity/brain/a22deae7-7753-458c-a40d-92e685f8af3e/.user_uploaded/media_1788628428702.jpg"
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    print("Enviando JSON workflow para o servidor Modal Z-Image...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="referencia_multi.jpg")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_zimage_multi_img2img.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)

