import modal
import os
import shutil
from huggingface_hub import hf_hub_download

app = modal.App("download-arena-models")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
arena_comfy_image = modal.Image.debian_slim().pip_install("huggingface-hub", "hf-transfer")

@app.function(
    image=arena_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=7200,  # 2 hours
    secrets=[modal.Secret.from_dict({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_XET_HIGH_PERFORMANCE": "1"})]
)
def download_all_models():
    # 1. QWEN
    print("Baixando Qwen-Image-Edit (VAE)...")
    os.makedirs("/comfyui_models/vae", exist_ok=True)
    hf_hub_download(
        repo_id="Comfy-Org/Qwen-Image_ComfyUI",
        filename="split_files/vae/qwen_image_vae.safetensors",
        local_dir="/tmp/qwen_dl"
    )
    shutil.move("/tmp/qwen_dl/split_files/vae/qwen_image_vae.safetensors", "/comfyui_models/vae/qwen_image_vae.safetensors")
    comfy_volume.commit()
    print("Qwen VAE salvo.")

    print("Baixando Qwen-Image-Edit (CLIP)...")
    os.makedirs("/comfyui_models/clip", exist_ok=True)
    hf_hub_download(
        repo_id="Comfy-Org/Qwen-Image_ComfyUI",
        filename="split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors",
        local_dir="/tmp/qwen_dl"
    )
    shutil.move("/tmp/qwen_dl/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors", "/comfyui_models/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors")
    comfy_volume.commit()
    print("Qwen CLIP salvo.")

    print("Baixando Qwen-Image-Edit (UNET)...")
    os.makedirs("/comfyui_models/unet", exist_ok=True)
    hf_hub_download(
        repo_id="Comfy-Org/Qwen-Image-Edit_ComfyUI",
        filename="split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors",
        local_dir="/tmp/qwen_dl"
    )
    shutil.move("/tmp/qwen_dl/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors", "/comfyui_models/unet/qwen_image_edit_2511_bf16.safetensors")
    comfy_volume.commit()
    print("Qwen UNET salvo.")

    # 2. Z-IMAGE
    print("Baixando Z-Image (VAE)...")
    os.makedirs("/comfyui_models/vae", exist_ok=True)
    hf_hub_download(
        repo_id="Comfy-Org/z_image_turbo",
        filename="split_files/vae/ae.safetensors",
        local_dir="/tmp/zimage_dl"
    )
    shutil.move("/tmp/zimage_dl/split_files/vae/ae.safetensors", "/comfyui_models/vae/z-image-ae.safetensors")
    comfy_volume.commit()
    print("Z-Image VAE salvo.")

    print("Baixando Z-Image (UNET)...")
    os.makedirs("/comfyui_models/unet", exist_ok=True)
    hf_hub_download(
        repo_id="Comfy-Org/z_image_turbo",
        filename="split_files/diffusion_models/z_image_turbo_bf16.safetensors",
        local_dir="/tmp/zimage_dl"
    )
    shutil.move("/tmp/zimage_dl/split_files/diffusion_models/z_image_turbo_bf16.safetensors", "/comfyui_models/unet/redzibDX1.safetensors")
    comfy_volume.commit()
    print("Z-Image UNET salvo.")

    # 3. HUNYUAN
    print("Baixando Hunyuan (VAE)...")
    os.makedirs("/comfyui_models/vae", exist_ok=True)
    hf_hub_download(
        repo_id="Kijai/HunyuanVideo_comfy",
        filename="hunyuan_video_vae_bf16.safetensors",
        local_dir="/tmp/hunyuan_dl"
    )
    shutil.move("/tmp/hunyuan_dl/hunyuan_video_vae_bf16.safetensors", "/comfyui_models/vae/hunyuan_vae.safetensors")
    comfy_volume.commit()
    print("Hunyuan VAE salvo.")

    print("Baixando Hunyuan (UNET)...")
    os.makedirs("/comfyui_models/unet", exist_ok=True)
    hf_hub_download(
        repo_id="Kijai/HunyuanVideo_comfy",
        filename="hunyuan_video_720_cfgdistill_fp8_e4m3fn.safetensors",
        local_dir="/tmp/hunyuan_dl"
    )
    shutil.move("/tmp/hunyuan_dl/hunyuan_video_720_cfgdistill_fp8_e4m3fn.safetensors", "/comfyui_models/unet/hunyuan_video_3.0_fp8.safetensors")
    comfy_volume.commit()
    print("Hunyuan UNET salvo.")

    print("TODOS OS MODELOS FORAM BAIXADOS E COPIADOS COM SUCESSO!")


@app.local_entrypoint()
def main():
    download_all_models.remote()
