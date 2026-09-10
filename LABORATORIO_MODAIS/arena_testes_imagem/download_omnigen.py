import modal
import os

app = modal.App("download-omnigen")
vol = modal.Volume.from_name("comfyui-models-vol")

# Re-use the existing image that has everything
image = modal.Image.debian_slim().pip_install("huggingface_hub", "hf_transfer")

@app.function(image=image, volumes={"/comfyui_models": vol}, timeout=3600)
def download_omnigen():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    print("Iniciando download do modelo OmniGen-v1 (Base)...")
    
    # OmniGen custom node usually expects the model in models/OmniGen/OmniGen-v1
    target_dir = "/comfyui_models/OmniGen/OmniGen-v1"
    os.makedirs(target_dir, exist_ok=True)
    
    snapshot_download(
        repo_id="shitao/OmniGen-v1",
        local_dir=target_dir,
        ignore_patterns=["*.msgpack", "*.h5", "coreml/*"]
    )
    print("Download do OmniGen concluído com sucesso!")
    vol.commit()

@app.local_entrypoint()
def main():
    download_omnigen.remote()
