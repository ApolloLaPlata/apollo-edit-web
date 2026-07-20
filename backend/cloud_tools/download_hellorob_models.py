import modal
import os
import subprocess
from huggingface_hub import hf_hub_download

app = modal.App("apollo-model-downloader-hellorob")
comfyui_models_vol = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
apollo_comfy_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "wget", "curl")
    .pip_install("huggingface_hub", "requests")
)

@app.function(
    image=image,
    volumes={
        "/comfyui/models": comfyui_models_vol,
        "/comfyui/apollo_models": apollo_comfy_volume
    },
    timeout=86400
)
def download_models():
    hf_models_to_download = [
        # (repo_id, filename, local_dir)
        ("Comfy-Org/z_image_turbo", "split_files/diffusion_models/z_image_turbo_bf16.safetensors", "/comfyui/apollo_models/diffusion_models"),
        ("Comfy-Org/z_image_turbo", "split_files/text_encoders/qwen_3_4b.safetensors", "/comfyui/apollo_models/text_encoders"),
        ("Comfy-Org/z_image_turbo", "split_files/vae/ae.safetensors", "/comfyui/apollo_models/vae"),
        ("numz/SeedVR2_comfyUI", "seedvr2_ema_7b_fp16.safetensors", "/comfyui/apollo_models/SEEDVR2"),
        ("numz/SeedVR2_comfyUI", "ema_vae_fp16.safetensors", "/comfyui/apollo_models/SEEDVR2"),
        ("RunDiffusion/Juggernaut-XL-v9", "Juggernaut-XL_v9_RunDiffusionPhoto_v2.safetensors", "/comfyui/models/checkpoints"),
        ("Bingsu/adetailer", "face_yolov8m.pt", "/comfyui/models/ultralytics/bbox"),
        ("FacehugmanSIR/8x_NMKD-Faces_160000_G", "8xNMKDFaces160000G_v10.pt", "/comfyui/models/upscale_models"),
    ]
    
    other_models = [
        ("https://civitai.com/api/download/models/788975", "/comfyui/models/loras/sdxl-skin_realism_acne_skin_details_imperfections.safetensors"),
        ("https://civitai.com/api/download/models/1271168", "/comfyui/models/loras/zimage-grainscape_ultrareal.safetensors")
    ]
    
    for repo_id, filename, local_dir in hf_models_to_download:
        os.makedirs(local_dir, exist_ok=True)
        # Using huggingface-cli for fast reliable downloads
        print(f"Downloading {filename} from {repo_id}...")
        try:
            downloaded_path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=local_dir,
                local_dir_use_symlinks=False
            )
            # rename if it downloaded to a subfolder
            if "/" in filename:
                base_name = os.path.basename(filename)
                old_path = os.path.join(local_dir, filename)
                new_path = os.path.join(local_dir, base_name)
                if os.path.exists(old_path) and old_path != new_path:
                    os.rename(old_path, new_path)
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

    for url, dest in other_models:
        dest_dir = os.path.dirname(dest)
        os.makedirs(dest_dir, exist_ok=True)
        if not os.path.exists(dest):
            print(f"Downloading {os.path.basename(dest)}...")
            cmd = ["curl", "-L", "-o", dest, url]
            try:
                subprocess.run(cmd, check=True)
            except Exception as e:
                print(f"Failed to download {os.path.basename(dest)}: {e}")
                
    comfyui_models_vol.commit()
    apollo_comfy_volume.commit()
    print("Download completed successfully!")

if __name__ == "__main__":
    download_models.remote()
