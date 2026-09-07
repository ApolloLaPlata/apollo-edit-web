
import modal
import base64
import uuid
import time
import os

from backend.cloud_tools.modal_app import app
from backend.cloud_tools.engines.apollo_arena_comfy_engine import ArenaComfyEngine

orchestrator_image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]", "pydantic", "requests", "langdetect", "Pillow")
    .add_local_python_source("backend")
)

# This acts as a high-level orchestrator class on Modal (CPU only, avoiding GPU deadlock!)
@app.cls(timeout=1800, min_containers=1, image=orchestrator_image)
class QwenImageEngine:
    
    @modal.enter()
    def setup(self):
        self.arena = ArenaComfyEngine()
        
    @modal.method()
    def generate(self, prompt: str, images_b64: list = None, aspect_ratio: str = "horizontal", use_upscale: bool = False, step_prompts: list = None, dynamic_steps: list = None):
        if not images_b64:
            images_b64 = []
            
        print(f"[QwenImageEngine] Inciando geracao com {len(images_b64)} imagens de referencia.")
        
        # Dimensions based on aspect ratio
        width, height = 1280, 720
        if aspect_ratio == "vertical": width, height = 720, 1280
        elif aspect_ratio == "square": width, height = 1024, 1024
        
        # Helper to run a ComfyUI pass via ArenaComfyEngine
        def run_pass(pass_prompt, img1=None, img2=None, img3=None, base_img=None):
            if base_img is None:
                from PIL import Image
                import io
                blank = Image.new("RGB", (width, height), (255, 255, 255))
                buf = io.BytesIO()
                blank.save(buf, format="PNG")
                base_img = base64.b64encode(buf.getvalue()).decode('utf-8')
                
            seed = int(time.time()) % 1000000
            wf = {
                "2":  { "class_type": "LoadImage", "inputs": { "image": "base_inpaint.png" }},
                "3": { "class_type": "CLIPLoader", "inputs": { "clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image" }},
                "4": { "class_type": "VAELoader", "inputs": { "vae_name": "qwen_image_vae.safetensors" }},
                "5":  { "class_type": "VAEEncode", "inputs": { "pixels": ["2", 0], "vae": ["4", 0] }},
                "6":  { "class_type": "TextEncodeQwenImageEditPlus", "inputs": {
                    "clip": ["3", 0], "prompt": pass_prompt, "vae": ["4", 0]
                }},
                "7":  { "class_type": "UNETLoader", "inputs": { "unet_name": "qwen_image_edit_2511_bf16.safetensors", "weight_dtype": "default" }},
                "8":  { "class_type": "ModelSamplingAuraFlow", "inputs": {
                    "model": ["7", 0], "shift": 3.1
                }},
                "9":  { "class_type": "CFGNorm", "inputs": {
                    "model": ["8", 0],
                    "strength": 1.0
                }},
                "10": { "class_type": "KSampler", "inputs": {
                    "seed": seed, "steps": 25, "cfg": 1, "sampler_name": "euler", "scheduler": "simple", "denoise": 1,
                    "model": ["9", 0],
                    "positive": ["6", 0],
                    "negative": ["6", 0],
                    "latent_image": ["5", 0]
                }},
                "11": { "class_type": "VAEDecode", "inputs": {
                    "samples": ["10", 0], "vae": ["4", 0]
                }},
                "12": { "class_type": "SaveImage", "inputs": {
                    "filename_prefix": "qwen_edit_out", "images": ["11", 0]
                }}
            }
            
            multi_dict = {}
            if img1:
                wf["5a"] = { "class_type": "LoadImage", "inputs": { "image": "img1.png" }}
                wf["6"]["inputs"]["image1"] = ["5a", 0]
                multi_dict["img1.png"] = img1
            
            if img2:
                wf["9a"] = { "class_type": "LoadImage", "inputs": { "image": "img2.png" }}
                wf["6"]["inputs"]["image2"] = ["9a", 0]
                multi_dict["img2.png"] = img2
                
            if img3:
                wf["13a"] = { "class_type": "LoadImage", "inputs": { "image": "img3.png" }}
                wf["6"]["inputs"]["image3"] = ["13a", 0]
                multi_dict["img3.png"] = img3

            try:
                res = self.arena.generate.remote(
                    workflow_json=wf,
                    source_image_b64=base_img,
                    source_image_name="base_inpaint.png" if base_img else "referencia.jpg",
                    multiple_images=multi_dict if multi_dict else None
                )
                if "image_b64" in res:
                    res["image_base64"] = res.pop("image_b64")
                return res
            except Exception as e:
                return {"status": "error", "error": str(e)}
                
        # -------------------------------------------------------------
        # MODES
        # -------------------------------------------------------------
        safe_prompt = prompt.replace('"', '\\"').replace('\n', ' ')
        
        # Fallback de dynamic_steps se o LLM nao retornar
        if not dynamic_steps:
            dynamic_steps = []
            num_images = len(images_b64)
            if num_images > 0:
                # Agrupa de 2 em 2 como padrao de seguranca (Qwen suporta ate 3, mas 2 e garantido)
                for i in range(0, num_images, 2):
                    indices = [i]
                    if i + 1 < num_images:
                        indices.append(i + 1)
                    
                    if i == 0:
                        p = f"Create a scene. {safe_prompt}. Add the characters from the reference images."
                    else:
                        p = f"EDIT THIS SCENE. Keep existing characters exactly as they are. Add the new characters from the reference images. {safe_prompt}"
                    
                    dynamic_steps.append({
                        "prompt": p,
                        "image_indices": indices
                    })

        # MODE 1: T2I (Text-to-Image)
        if len(images_b64) == 0:
            print("[QwenImageEngine] Mode: T2I (Pure, no dummy pixel)")
            
            from PIL import Image
            import io
            width, height = 1024, 1024
            if aspect_ratio == "horizontal": width, height = 1280, 720
            elif aspect_ratio == "vertical": width, height = 720, 1280
            
            blank = Image.new("RGB", (width, height), (255, 255, 255))
            buf = io.BytesIO()
            blank.save(buf, format="PNG")
            img1_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            
            # Precisamos do <|image_1|> no prompt para o TextEncodeQwenImageEditPlus processar
            if "<|image_1|>" not in prompt:
                prompt = "<|image_1|> " + prompt
                
            return run_pass(prompt, img1=img1_b64)
            
        # MODE 2: I2I (Single Character or Direct Edit)
        elif len(images_b64) == 1:
            print("[QwenImageEngine] Mode: I2I (1 Reference)")
            return run_pass(dynamic_steps[0]["prompt"] if dynamic_steps else prompt, img1=images_b64[0])
            
        # MODE 3: ITERATIVE MULTI-PASS (Dinâmico, suporta N inputs em pacotes de até 3)
        else:
            print(f"[QwenImageEngine] Mode: ITERATIVE ({len(images_b64)} References, {len(dynamic_steps)} Steps)")
            
            base_b64 = None
            last_res = None
            
            for step_idx, step in enumerate(dynamic_steps):
                p_prompt = step.get("prompt", safe_prompt)
                indices = step.get("image_indices", [])
                
                # Qwen suporta maximo de 3 imagens por pass
                img1 = images_b64[indices[0]] if len(indices) > 0 and indices[0] < len(images_b64) else None
                img2 = images_b64[indices[1]] if len(indices) > 1 and indices[1] < len(images_b64) else None
                img3 = images_b64[indices[2]] if len(indices) > 2 and indices[2] < len(images_b64) else None
                
                print(f"[QwenImageEngine] Running Pass {step_idx + 1}/{len(dynamic_steps)}... Indices: {indices} | Prompt: {p_prompt[:50]}...")
                
                res = run_pass(p_prompt, img1=img1, img2=img2, img3=img3, base_img=base_b64)
                if res.get("status") != "success":
                    print(f"[QwenImageEngine] Falha no Pass {step_idx + 1}. Abortando iteracao.")
                    return res
                
                base_b64 = res.get("image_base64")
                last_res = res
                
            return last_res
            
        return {"status": "error", "error": "Invalid state"}
