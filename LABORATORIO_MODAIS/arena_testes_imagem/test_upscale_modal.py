import json
import base64
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def upscale_image():
    print("Iniciando upscale 4x-UltraSharp...")
    
    # Simple Upscale Workflow
    workflow = {
        "1": { "class_type": "LoadImage", "inputs": { "image": "resultado_qwen_fixed.jpg" }},
        "2": { "class_type": "UpscaleModelLoader", "inputs": { "model_name": "4x-UltraSharp.pth" }},
        "3": { "class_type": "ImageUpscaleWithModel", "inputs": { "upscale_model": ["2", 0], "image": ["1", 0] }},
        "4": { "class_type": "ImageScaleBy", "inputs": { "upscale_method": "bicubic", "scale_by": 0.5, "image": ["3", 0] }},
        "5": { "class_type": "SaveImage", "inputs": { "images": ["4", 0], "filename_prefix": "qwen_upscaled" }}
    }
    
    engine = ArenaComfyEngine()
    
    img_path = "C:/Users/v5est/.gemini/antigravity/brain/a22deae7-7753-458c-a40d-92e685f8af3e/resultado_qwen_fixed.jpg"
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
    print("Enviando JSON workflow para o servidor Modal...")
    
    try:
        result = engine.generate.remote(workflow, source_image_b64=img_b64, source_image_name="resultado_qwen_fixed.jpg")
        
        if result.get("status") == "success":
            img_data = base64.b64decode(result["image_b64"])
            out_path = "C:/Users/v5est/.gemini/antigravity/brain/a22deae7-7753-458c-a40d-92e685f8af3e/resultado_qwen_upscaled.jpg"
            with open(out_path, "wb") as f:
                f.write(img_data)
            print(f"SUCESSO! Imagem salva em: {out_path}")
        else:
            print("Erro no servidor:", result)
            
    except Exception as e:
        print("Erro na execucao:", e)
