import modal
import os

app = modal.App("apollo-voice-models-downloader")
volume = modal.Volume.from_name("apollo-voice-models")

image = modal.Image.debian_slim().pip_install("huggingface_hub", "hf_transfer")

@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=3600,
    secrets=[modal.Secret.from_name("huggingface-secret")] # Assuming user has HF token, or we can download public models without it
)
def download_models():
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download
    
    models = [
        "Qwen/Qwen2-Audio-7B-Instruct",
        "fishaudio/fish-speech-1.5"
    ]
    
    for repo_id in models:
        print(f"Downloading {repo_id}...")
        try:
            # For public models
            model_dir = snapshot_download(
                repo_id=repo_id,
                local_dir=f"/data/{repo_id.split('/')[-1]}",
                ignore_patterns=["*.msgpack", "*.bin", "*.h5"] # prefer safetensors
            )
            print(f"Successfully downloaded {repo_id} to {model_dir}")
        except Exception as e:
            print(f"Error downloading {repo_id}: {e}")
            
    # Moshi uses a different repo, usually it's kyutai/moshika-tts5-7b
    try:
        print("Downloading kyutai/moshika-tts5-7b...")
        model_dir = snapshot_download(
            repo_id="kyutai/moshika-tts5-7b",
            local_dir="/data/moshika-tts5-7b",
            ignore_patterns=["*.msgpack", "*.bin", "*.h5"]
        )
        print("Successfully downloaded Moshi")
    except Exception as e:
        print(f"Error downloading Moshi: {e}")
        
    volume.commit()
    print("All models downloaded and volume committed!")

@app.local_entrypoint()
def main():
    download_models.remote()
