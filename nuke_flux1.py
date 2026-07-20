import codecs
import re

# 1. Rewrite flux_engine.py
flux_path = 'backend/cloud_tools/engines/flux_engine.py'
with codecs.open(flux_path, 'r', 'utf-8') as f:
    flux_content = f.read()

# We want to keep everything from the top down to the end of Flux2ComfyEngine.
# Flux2ComfyEngine ends right before class FluxSchnellEngine:
if 'class FluxSchnellEngine:' in flux_content:
    clean_flux = flux_content.split('class FluxSchnellEngine:')[0]
    # Remove the @app.cls before FluxSchnellEngine
    clean_flux = clean_flux.rsplit('@app.cls', 1)[0]
else:
    clean_flux = flux_content

# Also remove the flux_schnell_image, flux_dev_image, flux2_dev_python_image
# We can just build a completely new top part since we know exactly what we need.

new_flux_engine = '''"""
Apollo Modal Engine — FLUX 2 DEV
=================================================
Roda na GPU H100 via ComfyUI Headless.
Suporta aspect ratios (horizontal, vertical, square).
"""

import base64
import os
import traceback
import io
import time
import modal
import json
import subprocess
import requests
import urllib.request
from pathlib import Path

from backend.cloud_tools.modal_app import app

# Imagem Docker para o ComfyUI Headless (FLUX 2)
flux2_comfy_image = (
    modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10")
    .apt_install("git", "libgl1-mesa-glx", "libglib2.0-0")
    .pip_install(
        "torch==2.5.1",
        "torchvision==0.20.1",
        "torchaudio==2.5.1",
        "accelerate>=0.33.0",
        "huggingface_hub[hf_transfer]",
        "comfy-cli"
    )
    .add_local_file("Comfyui Workflow API/image_flux2/image_flux2.json", "/tmp/workflow.json", copy=True)
    .run_commands(
        [
            "comfy --workspace /comfyui install --nvidia",
            "comfy --workspace /comfyui node install-deps --workflow /tmp/workflow.json"
        ]
    )
    .env({
        "HF_HUB_OFFLINE": "0", 
        "TRANSFORMERS_OFFLINE": "0",
        "HF_HUB_ENABLE_HF_TRANSFER": "1"
    })
)

# Definir Volume para armazenar modelos (NFS de alta velocidade)
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(
    image=flux2_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=3600
)
def download_comfy_models():
    from huggingface_hub import hf_hub_download
    import os
    import shutil
    
    os.makedirs("/comfyui_models/unet", exist_ok=True)
    os.makedirs("/comfyui_models/clip", exist_ok=True)
    os.makedirs("/comfyui_models/vae", exist_ok=True)
    os.makedirs("/comfyui_models/loras", exist_ok=True)
    
    print('[DOWNLOAD] Baixando FLUX 2 FP8 para o Volume...')
    hf_hub_download(repo_id='Comfy-Org/flux2-dev', subfolder='split_files/diffusion_models', filename='flux2_dev_fp8mixed.safetensors', local_dir='/comfyui_models/unet', local_dir_use_symlinks=False)
    if os.path.exists('/comfyui_models/unet/split_files/diffusion_models/flux2_dev_fp8mixed.safetensors'):
        shutil.move('/comfyui_models/unet/split_files/diffusion_models/flux2_dev_fp8mixed.safetensors', '/comfyui_models/unet/flux2_dev_fp8mixed.safetensors')
        
    print('[DOWNLOAD] Baixando Mistral 3 CLIP para o Volume...')
    hf_hub_download(repo_id='Comfy-Org/flux2-dev', subfolder='split_files/text_encoders', filename='mistral_3_small_flux2_bf16.safetensors', local_dir='/comfyui_models/clip', local_dir_use_symlinks=False)
    if os.path.exists('/comfyui_models/clip/split_files/text_encoders/mistral_3_small_flux2_bf16.safetensors'):
        shutil.move('/comfyui_models/clip/split_files/text_encoders/mistral_3_small_flux2_bf16.safetensors', '/comfyui_models/clip/mistral_3_small_flux2_bf16.safetensors')
        
    print('[DOWNLOAD] Baixando VAE para o Volume...')
    hf_hub_download(repo_id='Comfy-Org/flux2-dev', subfolder='split_files/vae', filename='flux2-vae.safetensors', local_dir='/comfyui_models/vae', local_dir_use_symlinks=False)
    if os.path.exists('/comfyui_models/vae/split_files/vae/flux2-vae.safetensors'):
        shutil.move('/comfyui_models/vae/split_files/vae/flux2-vae.safetensors', '/comfyui_models/vae/full_encoder_small_decoder.safetensors')
        
    print('[DOWNLOAD] Baixando LoRA para o Volume...')
    hf_hub_download(repo_id='Comfy-Org/flux2-dev', subfolder='split_files/loras', filename='Flux_2-Turbo-LoRA_comfyui.safetensors', local_dir='/comfyui_models/loras', local_dir_use_symlinks=False)
    if os.path.exists('/comfyui_models/loras/split_files/loras/Flux_2-Turbo-LoRA_comfyui.safetensors'):
        shutil.move('/comfyui_models/loras/split_files/loras/Flux_2-Turbo-LoRA_comfyui.safetensors', '/comfyui_models/loras/Flux_2-Turbo-LoRA_comfyui.safetensors')
    
    print("[DOWNLOAD] Fazendo commit do Volume...")
    comfy_volume.commit()
    print("[DOWNLOAD] Todos os modelos baixados e armazenados no modal.Volume!")

FORMATS = {
    "horizontal": {"width": 1024, "height": 576},
    "vertical": {"width": 576, "height": 1024},
    "square": {"width": 768, "height": 768}
}

def wait_for_server(url, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False

@app.cls(gpu="h100", timeout=600, image=flux2_comfy_image, scaledown_window=120, volumes={"/comfyui_models": comfy_volume})
class Flux2ComfyEngine:
    @modal.enter()
    def load_model(self):
        import subprocess
        import os
        import json
        import urllib.request
        
        # Link models
        os.makedirs("/comfyui/models/unet", exist_ok=True)
        os.makedirs("/comfyui/models/clip", exist_ok=True)
        os.makedirs("/comfyui/models/vae", exist_ok=True)
        os.makedirs("/comfyui/models/loras", exist_ok=True)
        
        for f in os.listdir("/comfyui_models/unet"):
            if not os.path.exists(f"/comfyui/models/unet/{f}"): os.symlink(f"/comfyui_models/unet/{f}", f"/comfyui/models/unet/{f}")
        for f in os.listdir("/comfyui_models/clip"):
            if not os.path.exists(f"/comfyui/models/clip/{f}"): os.symlink(f"/comfyui_models/clip/{f}", f"/comfyui/models/clip/{f}")
        for f in os.listdir("/comfyui_models/vae"):
            if not os.path.exists(f"/comfyui/models/vae/{f}"): os.symlink(f"/comfyui/models/vae/{f}", f"/comfyui/models/vae/{f}")
        for f in os.listdir("/comfyui_models/loras"):
            if not os.path.exists(f"/comfyui/models/loras/{f}"): os.symlink(f"/comfyui/models/loras/{f}", f"/comfyui/models/loras/{f}")

        print("[Flux2ComfyEngine] Iniciando servidor ComfyUI headless com highvram...")
        self.server_process = subprocess.Popen(
            ["python", "main.py", "--listen", "127.0.0.1", "--port", "8188", "--highvram", "--fast"],
            cwd="/comfyui",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        if wait_for_server("http://127.0.0.1:8188/system_stats", timeout=120):
            print("[Flux2ComfyEngine] Servidor online! Iniciando PRE-WARMING (Cold Start interno)...")
            try:
                with open("/tmp/workflow.json", "r", encoding="utf-8") as f:
                    workflow = json.load(f)
                
                # Pre-warm: execute the graph with 1 step and tiny resolution just to force model load to VRAM
                for node_id, node in workflow.items():
                    if node["class_type"] == "EmptyFlux2LatentImage":
                        node["inputs"]["width"] = 256
                        node["inputs"]["height"] = 256
                    elif node["class_type"] == "PrimitiveInt" and node.get("_meta", {}).get("title") == "Steps":
                        node["inputs"]["value"] = 1
                
                req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": workflow}).encode("utf-8"), headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=300) # Give it 5 minutes to load weights to VRAM
                print("[Flux2ComfyEngine] PRE-WARMING concluido! GPU quente e pronta.")
            except Exception as e:
                print(f"[Flux2ComfyEngine] Falha no pre-warming (ignorado): {e}")
        else:
            raise RuntimeError("O servidor ComfyUI falhou ao iniciar no tempo limite.")

    @modal.method()
    def generate(self, prompt: str, aspect_ratio: str = "horizontal", seed: int = 42, reference_images_base64: list[str] = None) -> dict:
        import urllib.request
        import urllib.parse
        import json
        import time
        import traceback
        import base64
        
        t0 = time.time()
        print(f"[Flux2ComfyEngine] Request: {prompt[:50]}... | Formato: {aspect_ratio}")
        
        cfg = FORMATS.get(aspect_ratio.lower(), FORMATS["horizontal"])
        
        try:
            with open("/tmp/workflow.json", "r", encoding="utf-8") as f:
                workflow = json.load(f)
                
            input_image_path = None
            if reference_images_base64 and len(reference_images_base64) > 0:
                b64_data = reference_images_base64[0]
                if "," in b64_data:
                    b64_data = b64_data.split(",")[1]
                b64_data += "=" * ((4 - len(b64_data) % 4) % 4)
                img_data = base64.b64decode(b64_data)
                input_image_path = "/comfyui/input/image_flux2_input_image.png"
                with open(input_image_path, "wb") as img_f:
                    img_f.write(img_data)
                    
            for node_id, node in workflow.items():
                if node["class_type"] == "CLIPTextEncode":
                    if "text" in node["inputs"]:
                        node["inputs"]["text"] = prompt
                elif node["class_type"] == "RandomNoise":
                    node["inputs"]["noise_seed"] = seed % 1000000000000000
                elif node["class_type"] == "GetImageSize" or node["class_type"] == "EmptyFlux2LatentImage":
                    node["inputs"]["width"] = cfg["width"]
                    node["inputs"]["height"] = cfg["height"]
                    
            print("[Flux2ComfyEngine] Enviando job para API do ComfyUI...")
            req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=json.dumps({"prompt": workflow}).encode("utf-8"), headers={"Content-Type": "application/json"})
            resp = urllib.request.urlopen(req)
            resp_data = json.loads(resp.read().decode("utf-8"))
            prompt_id = resp_data["prompt_id"]
            
            print(f"[Flux2ComfyEngine] Job {prompt_id} criado, aguardando conclusao...")
            
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
                                print(f"[Flux2ComfyEngine] Geracao finalizada com sucesso em {render_time:.2f}s")
                                return {
                                    "status": "success",
                                    "image_base64": b64,
                                    "render_time_seconds": round(render_time, 2),
                                    "engine": "FLUX-2-COMFYUI-H100"
                                }
                except Exception as e:
                    pass
                time.sleep(2)
                
        except Exception as e:
            err = traceback.format_exc()
            print(f"[Flux2ComfyEngine] ERROR: {err}")
            return {
                "status": "error",
                "message": str(e),
                "traceback": err
            }
'''

with codecs.open(flux_path, 'w', 'utf-8') as f:
    f.write(new_flux_engine)

# 2. Rewrite apollo_modal_engine.py
router_path = 'backend/cloud_tools/apollo_modal_engine.py'
with codecs.open(router_path, 'r', 'utf-8') as f:
    router_content = f.read()

# Replace the api_generate_image function entirely
def replace_api_generate_image(content):
    import re
    # Match from @web_app.post("/generate/image") to the next @web_app.post
    pattern = r'(@web_app\.post\("/generate/image"\).*?)(?=@web_app\.post)'
    new_api = '''@web_app.post("/generate/image")
def api_generate_image(req: ImageRequest):
    import json
    try:
        model = req.model.lower()
        if model != "flux2-universal":
            return {"status": "error", "message": f"ERRO: Somente FLUX 2 DEV suportado (flux2-universal)."}
            
        from backend.cloud_tools.engines.flux_engine import Flux2ComfyEngine
        engine = Flux2ComfyEngine()
        print(f"[Router] Spawning Flux2ComfyEngine (H100) -> format: {req.format}")
        
        job = engine.generate.spawn(
            prompt=req.prompt,
            aspect_ratio=req.format,
            seed=req.seed,
            reference_images_base64=req.reference_images_base64
        )
        
        async def stream_result_comfyui():
            from modal.functions import FunctionCall
            fc = FunctionCall.from_id(job.object_id)
            while True:
                try:
                    res = await fc.get.aio(timeout=5.0)
                    yield json.dumps(res) + "\\n"
                    break
                except TimeoutError:
                    yield " \\n"
                except Exception as e:
                    yield json.dumps({"status": "error", "message": f"Erro na Modal: {str(e)}"}) + "\\n"
                    break
                    
        return StreamingResponse(stream_result_comfyui(), media_type="application/x-ndjson")
    
    except Exception as e:
        return {"status": "error", "message": f"Erro interno de Roteamento de Imagem: {str(e)}"}

'''
    return re.sub(pattern, new_api, content, flags=re.DOTALL)

new_router_content = replace_api_generate_image(router_content)
with codecs.open(router_path, 'w', 'utf-8') as f:
    f.write(new_router_content)

print("FLUX 1 DELETED. FLUX 2 ComfyUI Restored.")
