import modal
import os
from huggingface_hub import hf_hub_download
import shutil

app = modal.App("download-hunyuan-clip-fix")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    download.remote()

@app.function(
    image=modal.Image.debian_slim().pip_install("huggingface_hub"),
    volumes={"/vol": vol},
    timeout=7200
)
def download():
    print("Baixando text encoders corretos para Hunyuan 3.0...")
    os.makedirs("/vol/clip", exist_ok=True)
    os.makedirs("/tmp/dl", exist_ok=True)
    
    # LLaMA 3 8B (Comfy-Org repackaged fp8_scaled)
    llama = hf_hub_download(
        repo_id="Comfy-Org/HunyuanVideo_repackaged",
        filename="split_files/text_encoders/llava_llama3_fp8_scaled.safetensors",
        local_dir="/tmp/dl"
    )
    shutil.move(llama, "/vol/clip/llava_llama3_fp8_scaled.safetensors")
    
    # CLIP L (já tentei baixar, mas caso falhe no anterior, pego daqui)
    clip = hf_hub_download(
        repo_id="Comfy-Org/HunyuanVideo_repackaged",
        filename="split_files/text_encoders/clip_l.safetensors",
        local_dir="/tmp/dl"
    )
    shutil.move(clip, "/vol/clip/clip_l.safetensors")
    
    vol.commit()
    print("Text encoders do Hunyuan salvos!")
