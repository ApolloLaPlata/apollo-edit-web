import modal
import os
import urllib.request
import time

app = modal.App("download-qwen-fix")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("requests")
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

def download_file(url, dest_path):
    print(f"Baixando {url} para {dest_path}")
    if os.path.exists(dest_path):
        print(f"Arquivo {dest_path} ja existe, ignorando.")
        return
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        # Use urllib for large files to avoid loading into memory
        urllib.request.urlretrieve(url, dest_path)
        print(f"Download concluido: {dest_path}")
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")

@app.function(
    image=image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=14400,  # 4 hours
    scaledown_window=30
)
def download_qwen_models_direct():
    print("=== INICIANDO DOWNLOAD QWEN IMAGE EDIT (CORRECAO) ===")
    
    models_to_download = [
        # VAE
        ("https://huggingface.co/chenyang520/qwen_image_vae.safetensors/resolve/main/qwen_image_vae.safetensors", "/comfyui_models/vae/qwen_image_vae.safetensors"),
        # CLIP (Text Encoder)
        ("https://huggingface.co/TingFengYu/qwen_2.5_vl_7b_fp8_scaled.safetensors/resolve/main/qwen_2.5_vl_7b_fp8_scaled.safetensors", "/comfyui_models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors"),
        # UNET (Diffusion Model) - Using a mirror if possible, but let's use the main one if we can find it
        ("https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors", "/comfyui_models/checkpoints/qwen_image_edit_2511_bf16.safetensors")
    ]
    
    for url, dest in models_to_download:
        download_file(url, dest)
        
    print("Download finalizado! Salvando volume...")
    comfy_volume.commit()
    print("Sucesso!")

if __name__ == "__main__":
    with modal.runner.run_stub(app):
        download_qwen_models_direct.remote()
