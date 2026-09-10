import modal

app = modal.App("download-ace-step")
vol = modal.Volume.from_name("model-cache-vol", create_if_missing=True)

@app.function(volumes={"/apollo_volume": vol}, timeout=3600, image=modal.Image.debian_slim(python_version="3.10").pip_install("huggingface_hub", "hf_transfer"))
def download_models():
    import os
    os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    from huggingface_hub import snapshot_download

    base_path = "/apollo_volume/models/acestep"
    os.makedirs(base_path, exist_ok=True)
    
    xl_path = os.path.join(base_path, "acestep-v15-xl-sft")
    if not os.path.exists(xl_path):
        print(f"Baixando DiT XL SFT em {xl_path}...")
        snapshot_download("ACE-Step/acestep-v15-xl-sft", local_dir=xl_path)
    else:
        print(f"DiT XL SFT ja existe.")
        
    lm4b_path = os.path.join(base_path, "acestep-5Hz-lm-4B")
    if not os.path.exists(lm4b_path):
        print(f"Baixando LM 4B em {lm4b_path}...")
        snapshot_download("ACE-Step/acestep-5Hz-lm-4B", local_dir=lm4b_path)
    else:
        print(f"LM 4B ja existe.")

    print("Modelos concluidos.")

@app.local_entrypoint()
def main():
    download_models.remote()
