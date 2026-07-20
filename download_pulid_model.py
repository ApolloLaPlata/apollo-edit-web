import modal

app = modal.App("apollo_pulid_downloader")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(volumes={"/comfyui_models": comfy_volume}, timeout=3600)
def download_pulid():
    import urllib.request
    import os
    print("Baixando PuLID...")
    os.makedirs("/comfyui_models/pulid", exist_ok=True)
    pulid_path = "/comfyui_models/pulid/pulid_flux_v0.9.0.safetensors"
    if not os.path.exists(pulid_path):
        urllib.request.urlretrieve(
            "https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.0.safetensors",
            pulid_path
        )
        
    print("Baixando AntelopeV2...")
    insightface_dir = "/comfyui_models/insightface/models/antelopev2"
    os.makedirs(insightface_dir, exist_ok=True)
    
    zip_path = "/comfyui_models/insightface/models/antelopev2.zip"
    if not os.path.exists(os.path.join(insightface_dir, "1k3d68.onnx")):
        urllib.request.urlretrieve(
            "https://github.com/deepinsight/insightface/releases/download/v0.7/antelopev2.zip",
            zip_path
        )
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(insightface_dir)
        os.remove(zip_path)

    print("Download concluído!")

@app.local_entrypoint()
def main():
    download_pulid.remote()
