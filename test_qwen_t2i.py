
import json
import base64
import os
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

@app.local_entrypoint()
def test_qwen_t2i():
    print("Testando Qwen T2I sem plugar image1...")
    
    prompt = "A high-quality 8k cinematic photo of a solitary cyberpunk hacker typing on a neon keyboard."
    
    workflow = {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
        "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
        "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
        
        "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["3", 0], 
            "prompt": prompt, 
            "vae": ["4", 0]
            # OMITTING image1
        }},
        "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
        "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1280, "height": 720, "batch_size": 1 }},
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
            "seed": 12345, "steps": 25, "cfg": 2.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_t2i" }}
    }

    engine = ArenaComfyEngine()
    print("Executando...")
    res = engine.generate.remote(workflow, multiple_images={})
    print(res)


