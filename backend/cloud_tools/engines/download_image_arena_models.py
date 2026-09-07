import modal
import os

app = modal.App("download-image-arena-models")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(
    image=image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=7200,  # 2 hours for massive weights
    scaledown_window=30,
    secrets=[modal.Secret.from_name("huggingface-secret")]
)
def download_arena_models():
    from huggingface_hub import hf_hub_download, snapshot_download

    print("=== INICIANDO DOWNLOAD DOS PESOS PESADOS (ARENA DE IMAGEM) ===")

    # 1. Z-Image (Base / Foundation) - The high-quality non-turbo version
    print("\n[1/3] Baixando Z-Image (Base) da Tongyi-MAI...")
    snapshot_download(
        repo_id="Tongyi-MAI/Z-Image",
        local_dir="/comfyui_models/checkpoints/Z-Image-Base",
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
    )

    # 2. Hunyuan Image 3.0 - Tencent's monster
    print("\n[2/3] Baixando HunyuanImage-3.0...")
    snapshot_download(
        repo_id="tencent/HunyuanImage-3.0",
        local_dir="/comfyui_models/checkpoints/HunyuanImage-3",
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
    )
    
    # 3. Qwen (Representado aqui pelo Qwen2.5-VL ou Wanxiang/Qwen equivalentes)
    # Baixando os repositorios primarios de visao do Qwen 
    print("\n[3/3] Baixando arquitetura Qwen Base...")
    # placeholder for the exact Qwen Image safetensors path (using Qwen-VL base components)
    snapshot_download(
        repo_id="Qwen/Qwen2.5-VL-7B-Instruct",
        local_dir="/comfyui_models/checkpoints/Qwen-VL-Base",
        local_dir_use_symlinks=False,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot"]
    )

    print("\nDownloads completos! Persistindo volume da Arena...")
    comfy_volume.commit()
    print("Volume persistido com sucesso.")

if __name__ == "__main__":
    with modal.runner.run_stub(app):
        download_arena_models.remote()
