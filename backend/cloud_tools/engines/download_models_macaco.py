import modal
import os

app = modal.App("download-models-macaco")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=3600,
    secrets=[modal.Secret.from_name("huggingface-secret")]
)
def download_all_models():
    from huggingface_hub import hf_hub_download, snapshot_download

    print("Baixando Flux.1-dev...")
    hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-dev",
        filename="flux1-dev.safetensors",
        local_dir="/comfyui_models/unet",
        local_dir_use_symlinks=False
    )
    
    print("Baixando VAE...")
    hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-dev",
        filename="ae.safetensors",
        local_dir="/comfyui_models/vae",
        local_dir_use_symlinks=False
    )
    
    print("Baixando CLIP L...")
    hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="clip_l.safetensors",
        local_dir="/comfyui_models/clip",
        local_dir_use_symlinks=False
    )
    
    print("Baixando T5XXL fp16...")
    hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="t5xxl_fp16.safetensors",
        local_dir="/comfyui_models/clip",
        local_dir_use_symlinks=False
    )
    
    print("Baixando PuLID Flux v0.9.0...")
    hf_hub_download(
        repo_id="guozinan/PuLID",
        filename="pulid_flux_v0.9.0.safetensors",
        local_dir="/comfyui_models/pulid",
        local_dir_use_symlinks=False
    )
    
    print("Baixando EVA CLIP (Para o PuLID)...")
    hf_hub_download(
        repo_id="QuanSun/EVA-CLIP",
        filename="EVA02_CLIP_L_336_psz14_s6B.pt",
        local_dir="/comfyui_models/clip_vision",
        local_dir_use_symlinks=False
    )
    
    print("Baixando Antelopev2 (InsightFace para PuLID)...")
    snapshot_download(
        repo_id="DIAMONIK7777/antelopev2",
        local_dir="/comfyui_models/insightface/models/antelopev2",
        local_dir_use_symlinks=False
    )
    
    print("Baixando Flux Redux Adapter...")
    hf_hub_download(
        repo_id="black-forest-labs/FLUX.1-Redux-dev",
        filename="flux1-redux-dev.safetensors",
        local_dir="/comfyui_models/style_models",
        local_dir_use_symlinks=False
    )
    
    print("Baixando SigLIP (CLIP Vision do Redux)...")
    hf_hub_download(
        repo_id="Comfy-Org/sigclip_vision_384",
        filename="sigclip_vision_patch14_384.safetensors",
        local_dir="/comfyui_models/clip_vision",
        local_dir_use_symlinks=False
    )
    
    print("Downloads completos! Persistindo volume...")
    comfy_volume.commit()
    print("Volume persistido.")

if __name__ == "__main__":
    with modal.runner.run_stub(app):
        download_all_models.remote()
