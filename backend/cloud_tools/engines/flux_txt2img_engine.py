import modal
import os

flux2_txt2img_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "libgl1", "libglib2.0-0")
    .pip_install(
        "torch==2.4.0",
        "torchvision==0.19.0",
        "torchaudio==2.4.0",
        "xformers==0.0.27.post2",
        extra_options="--index-url https://download.pytorch.org/whl/cu121"
    )
    .pip_install(
        "transformers",
        "accelerate>=0.33.0",
        "huggingface_hub[hf_transfer]",
        "comfy-cli",
        "requests",
        "pillow"
    )
    .add_local_file("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/texto_flux2/image_flux2_text_to_image.json", "/tmp/workflow.json", copy=True)
    .run_commands(
        [
            "comfy --workspace /comfyui install --nvidia",
            "comfy --workspace /comfyui node install comfyui-tooling-nodes",
            "comfy --workspace /comfyui node install ComfyUI-Manager",
            "comfy --workspace /comfyui node install-deps --workflow /tmp/workflow.json"
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "0", 
        "TRANSFORMERS_OFFLINE": "0",
        "HF_HUB_ENABLE_HF_TRANSFER": "1"
    })
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

from backend.cloud_tools.modal_app import app

FORMATS = {
    "horizontal": {"width": 1280, "height": 720},
    "vertical": {"width": 720, "height": 1280},
    "square": {"width": 1024, "height": 1024},
}

from contextlib import contextmanager

@app.cls(
    gpu="H100", 
    image=flux2_txt2img_image,
    volumes={"/comfyui_models": comfy_volume},
    scaledown_window=60, 
    timeout=600,
    max_containers=5
)
class Flux2Txt2ImgEngine:
    @modal.enter()
    def load_model(self):
        import urllib.request
        import urllib.error
        import subprocess
        import time
        import sys
        
        yaml_content = "modal:\n  base_path: /comfyui_models\n  checkpoints: checkpoints\n  loras: loras\n  vae: vae\n  clip: clip\n  unet: unet\n  controlnet: controlnet\n"
        with open("/comfyui/extra_model_paths.yaml", "w") as f:
            f.write(yaml_content)
        
        print("[Flux2Txt2ImgEngine] Iniciando servidor ComfyUI headless...")
        self.comfy_process = subprocess.Popen(
            ["comfy", "--workspace", "/comfyui", "launch", "--", "--listen", "127.0.0.1", "--port", "8188"],
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        
        server_up = False
        for _ in range(180):
            try:
                with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=2):
                    server_up = True
                    break
            except Exception:
                time.sleep(1)
        
        if server_up:
            print("[Flux2Txt2ImgEngine] Servidor aguardando requisições.")
        else:
            raise RuntimeError("Falha no boot do ComfyUI no tempo limite.")

    @modal.method()
    def generate(self, prompt: str, aspect_ratio: str = "horizontal", **kwargs) -> dict:
        import urllib.request
        import urllib.parse
        import json
        import time
        import traceback
        import base64
        import os
        
        t0 = time.time()
        print(f"[Flux2Txt2ImgEngine] Request Txt2Img: {prompt[:50]}... | Formato: {aspect_ratio}")
        
        cfg = FORMATS.get(aspect_ratio.lower(), FORMATS["horizontal"])
        seed = kwargs.get("seed", 42)
        
        try:
            with open("/tmp/workflow.json", "r", encoding="utf-8") as f:
                workflow = json.load(f)
                
            # Mapeamento especifico do workflow de TEXT-TO-IMAGE
            # "98:6" -> CLIPTextEncode (Prompt Positivo)
            # "98:47" -> EmptyFlux2LatentImage (Width, Height) (Wait, might need to map to normal EmptyLatentImage)
            # "98:25" -> RandomNoise (noise_seed)
            if "98:6" in workflow and "text" in workflow["98:6"].get("inputs", {}):
                workflow["98:6"]["inputs"]["text"] = prompt
                
            if "98:47" in workflow and "width" in workflow["98:47"].get("inputs", {}):
                workflow["98:47"]["inputs"]["width"] = cfg["width"]
                workflow["98:47"]["inputs"]["height"] = cfg["height"]
                
            if "98:25" in workflow and "noise_seed" in workflow["98:25"].get("inputs", {}):
                workflow["98:25"]["inputs"]["noise_seed"] = seed % 1000000000000000
                
            # --- FIX: OVERRIDE MODEL NAMES TO MATCH WHAT IS ON MODAL VOLUME ---
            if "98:12" in workflow and "unet_name" in workflow["98:12"].get("inputs", {}):
                workflow["98:12"]["inputs"]["unet_name"] = "flux1-dev.safetensors"
            if "98:38" in workflow and "clip_name" in workflow["98:38"].get("inputs", {}):
                workflow["98:38"]["inputs"]["clip_name"] = "t5xxl_fp16.safetensors"
            if "98:10" in workflow and "vae_name" in workflow["98:10"].get("inputs", {}):
                workflow["98:10"]["inputs"]["vae_name"] = "ae.safetensors"
            
            # Since we don't have the Turbo LORA in Modal yet, we should disable the LORA node or ignore it.
            # The workflow uses a Switch(steps) "98:104" (Enable Turbo LoRA = false).
            # If "98:104" is false, the LORA node "98:101" might not execute, but ComfyUI STILL validates its inputs!
            # So we must replace the lora_name with a valid one if it exists, or just delete the node and bypass it.
            # Let's bypass it by deleting it from workflow if we don't have it, or give a dummy lora.
            # But the errors show that ComfyUI is validating "98:101" even if bypassed.
            # What LORAs do we have? ['sdxl-skin_realism_acne_skin_details_imperfections.safetensors', 'zimage-grainscape_ultrareal.safetensors']
            # We'll just set it to one of them so it passes validation (it won't be used anyway because switch is false).
            if "98:101" in workflow and "lora_name" in workflow["98:101"].get("inputs", {}):
                workflow["98:101"]["inputs"]["lora_name"] = "zimage-grainscape_ultrareal.safetensors"
                    
            print("[Flux2Txt2ImgEngine] Enviando job para API do ComfyUI...")
            req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": workflow}).encode("utf-8"), headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req)
            resp_data = json.loads(resp.read().decode("utf-8"))
            prompt_id = resp_data["prompt_id"]
            
            print(f"[Flux2Txt2ImgEngine] Job {prompt_id} criado, aguardando conclusao...")
            
            while True:
                hist_req = urllib.request.Request(f"http://127.0.0.1:8188/history/{prompt_id}")
                try:
                    hist_resp = urllib.request.urlopen(hist_req)
                    hist_data = json.loads(hist_resp.read().decode("utf-8"))
                    if prompt_id in hist_data:
                        outputs = hist_data[prompt_id].get("outputs", {})
                        if outputs:
                            output_node = list(outputs.keys())[0]
                            images = outputs[output_node].get("images", [])
                            if images:
                                out_filename = images[0]["filename"]
                                out_path = os.path.join("/comfyui/output", out_filename)
                                with open(out_path, "rb") as out_f:
                                    b64 = base64.b64encode(out_f.read()).decode("utf-8")
                                
                                render_time = time.time() - t0
                                print(f"[Flux2Txt2ImgEngine] Geracao finalizada com sucesso em {render_time:.2f}s")
                                return {
                                    "status": "success",
                                    "image_base64": b64,
                                    "render_time_seconds": round(render_time, 2),
                                    "engine": "FLUX-2-COMFYUI-H100-TXT2IMG"
                                }
                        
                        # Se chegou aqui, esta no history mas nao tem imagem (falhou ou OOM)
                        return {
                            "status": "error",
                            "message": f"Falha interna do ComfyUI. Workflow concluido sem imagens salvas. Historico: {json.dumps(hist_data[prompt_id])}"
                        }
                        
                except Exception as e:
                    pass
                
                # Timeout de segurança: 5 minutos
                if time.time() - t0 > 300:
                    return {
                        "status": "error",
                        "message": "Timeout de 5 minutos excedido aguardando o ComfyUI."
                    }
                time.sleep(2)
                
        except Exception as e:
            err = traceback.format_exc()
            body = ""
            if hasattr(e, "read"):
                try:
                    body = e.read().decode("utf-8")
                except:
                    pass
            print(f"[Flux2Txt2ImgEngine] ERROR: {err}\n[Flux2Txt2ImgEngine] BODY: {body}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": err,
                "body": body
            }
