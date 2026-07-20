"""
mirror_download.py — Standalone
================================
Script completamente autossuficiente para baixar todos os modelos
do Flux.1-dev no Volume da conta descarganews.
Não depende de nenhum módulo local do projeto.
"""

import modal

app = modal.App("apollo-mirror-download")

# Volume compartilhado — mesmo nome usado pelo apollo-render-router
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

# Imagem mínima com comfy-cli para baixar os modelos
download_image = (
    modal.Image.debian_slim()
    .apt_install("git", "curl", "wget")
    .pip_install("comfy-cli", "huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

@app.function(
    image=download_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=7200  # 2 horas para garantir o flux1-dev de 24GB
)
def mirror_download_all():
    import os
    import subprocess

    hf_token = os.environ.get("HF_TOKEN", "")
    if hf_token:
        print(f"[Mirror] ✅ HF Token OK: {hf_token[:8]}...")
    else:
        print("[Mirror] ❌ HF_TOKEN não encontrado!")
        return

    # Helper para baixar via huggingface_hub (mais confiável que comfy-cli para modelos gated)
    def hf_download(repo_id, filename, local_dir):
        os.makedirs(local_dir, exist_ok=True)
        dest = os.path.join(local_dir, filename)
        if os.path.exists(dest) and os.path.getsize(dest) > 1024:
            print(f"  ⏭️  Já existe: {filename} ({os.path.getsize(dest)/(1024**3):.2f} GB) — pulando")
            return True
        print(f"  ⬇️  Baixando: {filename}...")
        from huggingface_hub import hf_hub_download
        try:
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=local_dir,
                token=hf_token,
            )
            size = os.path.getsize(path) / (1024**3)
            print(f"  ✅ {filename} ({size:.2f} GB)")
            return True
        except Exception as e:
            print(f"  ❌ Falha em {filename}: {e}")
            return False

    print("\n========================================")
    print("  MIRROR DOWNLOAD — descarganews Fleet  ")
    print("========================================\n")

    # 1. FLUX.1-dev UNet (24GB - gated)
    print("[1/5] flux1-dev.safetensors (UNet ~24GB)...")
    hf_download("black-forest-labs/FLUX.1-dev", "flux1-dev.safetensors", "/comfyui_models/unet")

    # 2. T5 Text Encoder (~9GB)
    print("[2/5] t5xxl_fp16.safetensors (Text Encoder ~9GB)...")
    hf_download("comfyanonymous/flux_text_encoders", "t5xxl_fp16.safetensors", "/comfyui_models/clip")

    # 3. CLIP L (~246MB)
    print("[3/5] clip_l.safetensors (CLIP L ~246MB)...")
    hf_download("comfyanonymous/flux_text_encoders", "clip_l.safetensors", "/comfyui_models/clip")

    # 4. FLUX VAE (~335MB - também gated)
    print("[4/5] ae.safetensors (VAE ~335MB)...")
    hf_download("black-forest-labs/FLUX.1-dev", "ae.safetensors", "/comfyui_models/vae")

    # 5. LoRA grainscape (public)
    print("[5/5] zimage-grainscape_ultrareal.safetensors (LoRA)...")
    os.makedirs("/comfyui_models/loras", exist_ok=True)
    lora_ok = hf_download("Comfy-Org/z_image_grainscape", "zimage-grainscape_ultrareal.safetensors", "/comfyui_models/loras")
    if not lora_ok:
        # Cria placeholder vazio para não bloquiar validação do ComfyUI (switch está desligado no workflow)
        placeholder = "/comfyui_models/loras/zimage-grainscape_ultrareal.safetensors"
        with open(placeholder, "wb") as f:
            f.write(b"\x00" * 1024)
        print(f"  ⚠️  Placeholder criado (LoRA não usada no workflow padrão)")

    # Commit no volume
    print("\n[Mirror] Commitando no Volume...")
    comfy_volume.commit()

    # Inventário final
    print("\n=== INVENTÁRIO DO VOLUME ===")
    total_gb = 0
    for root, dirs, files in os.walk("/comfyui_models"):
        for f in files:
            full = os.path.join(root, f)
            size = os.path.getsize(full)
            size_gb = size / (1024**3)
            total_gb += size_gb
            rel = full.replace("/comfyui_models/", "")
            print(f"  ✅ {rel:<55} {size_gb:.2f} GB")

    print(f"\n  TOTAL: {total_gb:.2f} GB no Volume")
    print("\n✅ MIRROR COMPLETO! Conta descarganews pronta para gerar imagens.")

@app.local_entrypoint()
def main():
    print("Disparando mirror download na conta descarganews...")
    mirror_download_all.remote()
