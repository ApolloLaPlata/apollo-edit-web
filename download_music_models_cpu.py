import modal
import os
import sys

app = modal.App("apollo-music-downloader")

volume_models = modal.Volume.from_name("apollo-models", create_if_missing=True)
volume_cache = modal.Volume.from_name("model-cache-vol", create_if_missing=True)
volume_comfy = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

@app.function(image=image, volumes={"/models": volume_models, "/apollo_volume": volume_cache, "/apollo_comfy": volume_comfy}, timeout=3600, secrets=[modal.Secret.from_name("huggingface-secret")])
def download_all_music_models():
    from huggingface_hub import snapshot_download, hf_hub_download, login
    import os
    
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    token = os.environ.get("HF_TOKEN")
    if token:
        login(token)

    print("1. Baixando MiniMax-Music3 para apollo-models...")
    snapshot_download("MiniMaxAI/MiniMax-Music3", cache_dir="/models/huggingface_cache")
    
    print("2. Baixando Stable Audio 3 Medium para apollo-models...")
    hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model_config.json", cache_dir="/models/huggingface_cache")
    hf_hub_download(repo_id="stabilityai/stable-audio-3-medium", filename="model.safetensors", cache_dir="/models/huggingface_cache")
    
    print("3. Baixando ACE-Step 1.5 para model-cache-vol...")
    base_path = "/apollo_volume/models/acestep"
    os.makedirs(base_path, exist_ok=True)
    snapshot_download("ACE-Step/Ace-Step1.5", local_dir=os.path.join(base_path, "Ace-Step1.5"))
    snapshot_download("ACE-Step/acestep-v15-xl-sft", local_dir=os.path.join(base_path, "acestep-v15-xl-sft"))
    snapshot_download("ACE-Step/acestep-5Hz-lm-4B", local_dir=os.path.join(base_path, "acestep-5Hz-lm-4B"))

    print("=== TODOS OS MODELOS DE MUSICA FORAM BAIXADOS COM SUCESSO (VIA CPU) ===")
