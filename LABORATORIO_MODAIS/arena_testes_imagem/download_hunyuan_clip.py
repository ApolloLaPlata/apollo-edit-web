import modal
import os
from huggingface_hub import hf_hub_download
import shutil

app = modal.App("download-hunyuan-clip")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    download.remote()

@app.function(
    image=modal.Image.debian_slim().pip_install("huggingface_hub"),
    volumes={"/vol": vol},
    timeout=7200 # 2 hours because LLaMA is huge
)
def download():
    print("Baixando text encoders para Hunyuan 3.0...")
    os.makedirs("/vol/clip", exist_ok=True)
    os.makedirs("/tmp/dl", exist_ok=True)
    
    # Baixar CLIP L
    clip_l = hf_hub_download(
        repo_id="comfyanonymous/flux_text_encoders",
        filename="clip_l.safetensors",
        local_dir="/tmp/dl"
    )
    shutil.move(clip_l, "/vol/clip/clip_l.safetensors")
    
    # Baixar LLaMA 3 8B (usando versão fp8 para ser mais rapido/leve)
    llama = hf_hub_download(
        repo_id="Kijai/HunyuanVideo_comfy",
        filename="llava_llama3_8b_text_encoder_fp8_e4m3fn.safetensors",
        local_dir="/tmp/dl"
    )
    shutil.move(llama, "/vol/clip/llava_llama3_8b_text_encoder_fp8_e4m3fn.safetensors")
    
    vol.commit()
    print("Text encoders do Hunyuan salvos!")
