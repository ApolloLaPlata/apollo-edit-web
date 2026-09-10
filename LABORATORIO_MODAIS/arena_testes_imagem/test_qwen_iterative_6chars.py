
import json
import base64
import uuid
import os
import time

from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine, app

def create_workflow(image1_name, image2_name, image3_name, prompt):
    return {
        "1": { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
        "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
        "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
        
        "5a": { "class_type": "LoadImage", "inputs": { "image": image1_name }},
        "5b": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5a", 0] }},
        
        "5c": { "class_type": "LoadImage", "inputs": { "image": image2_name }},
        "5d": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5c", 0] }},

        "5e": { "class_type": "LoadImage", "inputs": { "image": image3_name }},
        "5f": { "class_type": "FluxKontextImageScale", "inputs": { "image": ["5e", 0] }},
        
        "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
            "clip": ["3", 0], 
            "prompt": prompt, 
            "vae": ["4", 0], 
            "image1": ["5b", 0],
            "image2": ["5d", 0],
            "image3": ["5f", 0]
        }},
        "7": { "class_type": "ConditioningZeroOut", "inputs": { "conditioning": ["6", 0] }},
        "8":  { "class_type": "EmptyLatentImage", "inputs": { "width": 1400, "height": 720, "batch_size": 1 }},
        "9": { "class_type": "KSampler", "inputs": {
            "model": ["1", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["8", 0],
            "seed": int(time.time()), "steps": 25, "cfg": 2.5, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0
        }},
        "10": { "class_type": "VAEDecode", "inputs": { "samples": ["9", 0], "vae": ["4", 0] }},
        "11": { "class_type": "SaveImage", "inputs": { "images": ["10", 0], "filename_prefix": "qwen_iterative" }}
    }

def read_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def save_b64(b64_data, path):
    with open(path, "wb") as f:
        f.write(base64.b64decode(b64_data))

@app.local_entrypoint()
def test_qwen_iterative():
    print("Iniciando Pipeline de Acumulo de Personagens (6 chars)...")
    engine = ArenaComfyEngine()
    
    # Paths
    base_dir = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/arena_testes_imagem"
    c1 = read_b64(f"{base_dir}/char1_turnaround.png")
    c2 = read_b64(f"{base_dir}/char2_turnaround.png")
    c3 = read_b64(f"{base_dir}/char3_turnaround.png")
    c4 = read_b64(f"{base_dir}/char4_turnaround.png")
    c5 = read_b64(f"{base_dir}/char5_turnaround.png")
    c6 = read_b64(f"{base_dir}/char6_turnaround.png")
    
    # --- PASS 1 ---
    print(">>> PASS 1: Gerando char1 e char2 no cenario...")
    p1_img1 = f"pass1_i1_{uuid.uuid4().hex[:4]}.png"
    p1_img2 = f"pass1_i2_{uuid.uuid4().hex[:4]}.png"
    p1_img3 = f"pass1_i3_{uuid.uuid4().hex[:4]}.png" # dummy for the 3rd slot
    
    prompt1 = (
        "A dynamic 2d animation style scene in a futuristic cyberpunk city alley with neon lights. "
        "Two distinct characters are standing on the left side of the screen. "
        "Character 1 (image1) is far left, FACING FORWARD, FRONT VIEW, looking at camera. "
        "Character 2 (image2) is center left, FACING FORWARD, FRONT VIEW, looking at camera. "
        "The right side of the screen is empty background. "
        "DO NOT MIX FACIAL FEATURES. Each character MUST strictly match their reference image front view. Vibrant colors, highly detailed."
    )
    
    wf1 = create_workflow(p1_img1, p1_img2, p1_img3, prompt1)
    res1 = engine.generate.remote(wf1, multiple_images={p1_img1: c1, p1_img2: c2, p1_img3: c2})
    if res1.get("status") == "success":
        scene_b64 = res1["image_b64"]
        save_b64(scene_b64, f"{base_dir}/iterative_step1.png")
        print("PASS 1 Concluido! iterative_step1.png salvo.")
    else:
        print("Erro Pass 1:", res1)
        return
        
    # --- PASS 2 ---
    print(">>> PASS 2: Injetando char3 e char4 na cena base...")
    p2_img1 = f"pass2_i1_{uuid.uuid4().hex[:4]}.png" # scene
    p2_img2 = f"pass2_i2_{uuid.uuid4().hex[:4]}.png" # char3
    p2_img3 = f"pass2_i3_{uuid.uuid4().hex[:4]}.png" # char4
    
    prompt2 = (
        "EDIT THIS SCENE (image1). Keep the background and the two existing characters on the left exactly as they are. "
        "Add two NEW characters to the right side of the screen: "
        "Character 3 (image2) in the center right, FACING FORWARD, FRONT VIEW. "
        "Character 4 (image3) on the far right, FACING FORWARD, FRONT VIEW. "
        "DO NOT modify or alter the original characters from image1. "
        "DO NOT MIX FACIAL FEATURES. Vibrant colors, highly detailed 2d animation style."
    )
    
    wf2 = create_workflow(p2_img1, p2_img2, p2_img3, prompt2)
    res2 = engine.generate.remote(wf2, multiple_images={p2_img1: scene_b64, p2_img2: c3, p2_img3: c4})
    if res2.get("status") == "success":
        scene_b64 = res2["image_b64"]
        save_b64(scene_b64, f"{base_dir}/iterative_step2.png")
        print("PASS 2 Concluido! iterative_step2.png salvo.")
    else:
        print("Erro Pass 2:", res2)
        return

    # --- PASS 3 ---
    print(">>> PASS 3: Injetando char5 e char6 na cena base...")
    p3_img1 = f"pass3_i1_{uuid.uuid4().hex[:4]}.png" # scene
    p3_img2 = f"pass3_i2_{uuid.uuid4().hex[:4]}.png" # char5
    p3_img3 = f"pass3_i3_{uuid.uuid4().hex[:4]}.png" # char6
    
    prompt3 = (
        "EDIT THIS SCENE (image1). Keep the background and the four existing characters exactly as they are. "
        "Add two MORE NEW characters in the background alley behind the others: "
        "Character 5 (image2) standing in the background left, FACING FORWARD, FRONT VIEW. "
        "Character 6 (image3) standing in the background right, FACING FORWARD, FRONT VIEW. "
        "DO NOT modify or alter the four original characters in the foreground from image1. "
        "DO NOT MIX FACIAL FEATURES. Vibrant colors, highly detailed 2d animation style."
    )
    
    wf3 = create_workflow(p3_img1, p3_img2, p3_img3, prompt3)
    res3 = engine.generate.remote(wf3, multiple_images={p3_img1: scene_b64, p3_img2: c5, p3_img3: c6})
    if res3.get("status") == "success":
        scene_b64 = res3["image_b64"]
        save_b64(scene_b64, f"{base_dir}/iterative_step3_FINAL.png")
        print("PASS 3 Concluido! iterative_step3_FINAL.png salvo. Pipeline de Acumulo finalizado!")
    else:
        print("Erro Pass 3:", res3)
        return

