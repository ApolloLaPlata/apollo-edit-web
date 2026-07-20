import modal
import os

app = modal.App("apollo-setup-models")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

flux2_comfy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

@app.function(
    image=flux2_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=3600
)
def download_comfy_models_laplata():
    from huggingface_hub import hf_hub_download
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

if __name__ == "__main__":
    download_comfy_models_laplata.remote()
