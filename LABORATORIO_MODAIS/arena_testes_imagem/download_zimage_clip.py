import modal
import os
from huggingface_hub import hf_hub_download
import shutil

app = modal.App("download-zimage-clip")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    download.remote()

@app.function(
    image=modal.Image.debian_slim().pip_install("huggingface_hub"),
    volumes={"/vol": vol},
    timeout=3600
)
def download():
    print("Baixando qwen_3_4b.safetensors para Z-Image...")
    os.makedirs("/vol/clip", exist_ok=True)
    os.makedirs("/tmp/dl", exist_ok=True)
    
    file_path = hf_hub_download(
        repo_id="Comfy-Org/z_image_turbo",
        filename="split_files/text_encoders/qwen_3_4b.safetensors",
        local_dir="/tmp/dl"
    )
    
    dest_path = "/vol/clip/qwen_3_4b.safetensors"
    shutil.move(file_path, dest_path)
    vol.commit()
    print("Download concluido! Arquivo salvo em:", dest_path)
