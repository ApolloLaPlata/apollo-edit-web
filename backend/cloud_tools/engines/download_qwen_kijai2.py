import modal
import os

app = modal.App("download-qwen-kijai2")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=14400,
    scaledown_window=30
)
def download_qwen_models_direct():
    from huggingface_hub import hf_hub_download
    import shutil
    
    print("=== INICIANDO DOWNLOAD QWEN KIJAI VIA HF_HUB ===")
    
    # Text Encoder
    print("Baixando CLIP...")
    downloaded_path = hf_hub_download(
        repo_id="Kijai/QwenImage_experimental",
        filename="Qwen_Image_fp8_e5m2_scaled_KJ.safetensors",
        local_dir="/comfyui_models/clip",
        local_dir_use_symlinks=False
    )
    
    # Rename to the expected name
    final_path = "/comfyui_models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors"
    if os.path.exists(final_path):
        os.remove(final_path)
    os.rename(downloaded_path, final_path)
    
    print("Download finalizado! Salvando volume...")
    comfy_volume.commit()
    print("Sucesso!")

if __name__ == "__main__":
    download_qwen_models_direct.remote()
