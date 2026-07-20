import modal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append("/root")
sys.path.append("/pkg")
sys.path.append("/")

from backend.cloud_tools.engines.universal_engine import universal_comfy_image, comfy_volume
from backend.cloud_tools.modal_app import app

@app.function(
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=3600
)
def download_models():
    print("[Universal Downloader] Iniciando download de modelos para o Volume...")
    # FLUX.1 VAE
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors --relative-path models/vae")
    
    # FLUX.1 Dev UNet Original
    # os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors --relative-path models/unet")
    
    # PuLID (Consistencia de Personagem)
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.0.safetensors --relative-path models/pulid")
    
    # KLEIN 4B
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8/resolve/main/flux-2-klein-base-4b-fp8.safetensors --relative-path models/diffusion_models")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/qwen_3_4b.safetensors --relative-path models/text_encoders")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors --relative-path models/vae")
    
    # Aqui o Diretor podera adicionar links de LORAs, Checkpoints SDXL, etc.
    print("[Universal Downloader] Downloads finalizados!")

@app.function(
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=3600
)
def download_ultrasharp():
    print("[Universal Downloader] Downloading 4x-UltraSharp...")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/lokcx/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth --relative-path models/upscale_models")
    print("[Universal Downloader] Download finished!")
