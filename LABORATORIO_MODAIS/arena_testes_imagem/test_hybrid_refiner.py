import json
import base64
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_zimage_refiner_modal():
    print("Iniciando Z-Image Refiner sobre a imagem do Qwen...")
    
    # Workflow Z-Image Img2Img
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "redzibDX1.safetensors", "weight_dtype": "fp8_e4m3fn" }},
        "2": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_3_4b.safetensors", "type": "lumina2" }},
        "3": { "class_type": "VAELoader", "inputs": { "vae_name": "ae.safetensors" }},
        
        # Load Image and VAE Encode (Usando a imagem gerada pelo Qwen!)
        "4": { "class_type": "LoadImage", "inputs": { "image": "resultado_modal_qwen.jpg" }},
        "5": { "class_type": "VAEEncode", "inputs": { "pixels": ["4", 0], "vae": ["3", 0] }},
        
        # Text Prompts (Adicionando tags de ultra realismo)
        "6": { "class_type": "CLIPTextEncode", "inputs": { "text": "a cinematic photo of a muscular man wearing a black beanie and punisher tank top, riding a mountain bike on a sunny beach boardwalk, ultra detailed, hyperrealistic, 8k resolution, sharp focus, skin pores, realistic textures, photograph", "clip": ["2", 0] }},
        "7": { "class_type": "CLIPTextEncode", "inputs": { "text": "bad quality, blurry, deformed, weird anatomy, pastel, painting, illustration, smooth skin", "clip": ["2", 0] }},
        
        # Sampler (Denoise 0.35 para refinar textura sem mudar o rosto/composicao)
        "8": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
            "seed": 999, "steps": 30, "cfg": 4.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 0.35
        }},
        
        "9": { "class_type": "VAEDecode", "inputs": { "samples": ["8", 0], "vae": ["3", 0] }},
        "10": { "class_type": "SaveImage", "inputs": { "images": ["9", 0], "filename_prefix": "qwen_zimage_refined" }}
    }

    engine = ArenaComfyEngine()
    
    img_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_modal_qwen.jpg"
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    print("Enviando JSON workflow para o servidor Modal...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="resultado_modal_qwen.jpg")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem/resultado_hibrido_qwen_zimage.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)
