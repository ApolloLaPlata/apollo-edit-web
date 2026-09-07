import modal
import os

app = modal.App("download-qwen-image-models")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=14400,  # 4 hours
    scaledown_window=30
)
def download_qwen_models():
    from huggingface_hub import hf_hub_download
    
    print("=== INICIANDO DOWNLOAD QWEN IMAGE EDIT (41GB) ===")
    
    repo_id = "Comfy-Org/Qwen-Image-Edit_ComfyUI"

    # 1. Diffusion Model (UNET) - 41GB!
    print("Baixando UNET principal...")
    hf_hub_download(
        repo_id=repo_id,
        filename="split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors",
        local_dir="/comfyui_models/checkpoints", # Placing in checkpoints for ModelLoader
        local_dir_use_symlinks=False
    )
    # Move from the nested folder to root of checkpoints
    os.rename("/comfyui_models/checkpoints/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors", "/comfyui_models/checkpoints/qwen_image_edit_2511_bf16.safetensors")

    # 2. Text Encoder (CLIP)
    print("Baixando CLIP...")
    hf_hub_download(
        repo_id=repo_id,
        filename="split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        local_dir="/comfyui_models/clip",
        local_dir_use_symlinks=False
    )
    os.rename("/comfyui_models/clip/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors", "/comfyui_models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors")

    # 3. VAE
    print("Baixando VAE...")
    hf_hub_download(
        repo_id=repo_id,
        filename="split_files/vae/qwen_image_vae.safetensors",
        local_dir="/comfyui_models/vae",
        local_dir_use_symlinks=False
    )
    os.rename("/comfyui_models/vae/split_files/vae/qwen_image_vae.safetensors", "/comfyui_models/vae/qwen_image_vae.safetensors")
    
    print("Download finalizado! Salvando volume...")
    comfy_volume.commit()
    print("Sucesso!")

if __name__ == "__main__":
    with modal.runner.run_stub(app):
        download_qwen_models.remote()
