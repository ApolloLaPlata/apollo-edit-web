import modal
import os
import sys

apollo_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

app = modal.App("yue-downloader")

yue_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("huggingface_hub", "hf-transfer")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

@app.function(image=yue_image, volumes={"/apollo_volume": apollo_volume}, timeout=3600, secrets=[modal.Secret.from_name("huggingface-secret")])
def download_yue():
    from huggingface_hub import snapshot_download
    import os
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
    
    base_dir = "/apollo_volume/models/yue"
    os.makedirs(base_dir, exist_ok=True)
    
    print("Iniciando download do m-a-p/YuE-s1-7B-anneal-en-cot...")
    snapshot_download("m-a-p/YuE-s1-7B-anneal-en-cot", local_dir=f"{base_dir}/YuE-s1-7B-anneal-en-cot")
    print("Sucesso! Baixando m-a-p/YuE-s2-1B-general...")
    snapshot_download("m-a-p/YuE-s2-1B-general", local_dir=f"{base_dir}/YuE-s2-1B-general")
    print("Sucesso! Baixando m-a-p/xcodec_mini_infer...")
    snapshot_download("m-a-p/xcodec_mini_infer", local_dir=f"{base_dir}/xcodec_mini_infer")
    
    print("TODOS OS PESOS DO YUE FORAM BAIXADOS COM SUCESSO NO VOLUME PERSISTENTE!")

@app.local_entrypoint()
def main():
    print("Iniciando rotina de download para o apollo_volume...")
    download_yue.remote()
