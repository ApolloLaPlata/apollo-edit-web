import modal
import os
import urllib.request

app = modal.App("download-qwen-kijai")

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
    print("=== INICIANDO DOWNLOAD QWEN KIJAI ===")
    
    models_to_download = [
        # VAE
        ("https://huggingface.co/Kijai/QwenImage_experimental/resolve/main/qwen_image_HDR_vae_fp32_comfy.safetensors", "/comfyui_models/vae/qwen_image_vae.safetensors"),
        # CLIP (Text Encoder)
        ("https://huggingface.co/Kijai/QwenImage_experimental/resolve/main/Qwen_Image_fp8_e5m2_scaled_KJ.safetensors", "/comfyui_models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors"),
    ]
    
    for url, dest in models_to_download:
        download_file(url, dest)
        
    print("Download finalizado! Salvando volume...")
    comfy_volume.commit()
    print("Sucesso!")

if __name__ == "__main__":
    download_qwen_models_direct.remote()
