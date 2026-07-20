"""
download_pulid_models.py — Standalone
======================================
Baixa os modelos necessários para o workflow PuLID + Redux
que mantém consistência de identidade dos personagens.

Modelos necessários:
  - pulid_flux_v0.9.1.safetensors  → PuLID (identidade facial)
  - flux1-redux-dev.safetensors    → Redux (referência visual global)
  - EVA-CLIP (embutido no PuLID node)
  - InsightFace (via ComfyUI node)
"""

import modal

app = modal.App("apollo-pulid-download")

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

download_image = (
    modal.Image.debian_slim()
    .apt_install("git", "curl")
    .pip_install("huggingface_hub[hf_transfer]")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

@app.function(
    image=download_image,
    volumes={"/comfyui_models": comfy_volume},
    secrets=[modal.Secret.from_name("huggingface-secret")],
    timeout=7200
)
def download_pulid_and_redux():
    import os
    from huggingface_hub import hf_hub_download

    hf_token = os.environ.get("HF_TOKEN", "")
    print(f"[PuLID Download] HF Token: {hf_token[:8]}...")

    def dl(repo_id, filename, local_dir, token=None):
        os.makedirs(local_dir, exist_ok=True)
        dest = os.path.join(local_dir, filename)
        if os.path.exists(dest) and os.path.getsize(dest) > 1024 * 1024:
            size_gb = os.path.getsize(dest) / (1024**3)
            print(f"  ⏭️  Já existe: {filename} ({size_gb:.2f} GB)")
            return True
        print(f"  ⬇️  Baixando: {filename}...")
        try:
            path = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                local_dir=local_dir,
                token=token or hf_token,
            )
            size_gb = os.path.getsize(path) / (1024**3)
            print(f"  ✅ {filename} ({size_gb:.2f} GB)")
            return True
        except Exception as e:
            print(f"  ❌ Falha: {filename} → {e}")
            return False

    print("\n==================================================")
    print("  DOWNLOAD: PuLID + Redux (Consistência Visual)   ")
    print("==================================================\n")

    # 1. PuLID para Flux.1-dev (identidade facial/personagem)
    print("[1/3] PuLID Flux v0.9.1 (~700MB)...")
    ok = dl("guozinan/PuLID", "pulid_flux_v0.9.1.safetensors", "/comfyui_models/pulid")
    if not ok:
        # tenta versão anterior
        dl("guozinan/PuLID", "pulid_flux_v0.9.0.safetensors", "/comfyui_models/pulid")

    # 2. Flux Redux Dev (condicionamento por imagem de referência)
    print("[2/3] Flux1-Redux-Dev (~3.1GB)...")
    dl("black-forest-labs/FLUX.1-Redux-dev", "flux1-redux-dev.safetensors", 
       "/comfyui_models/style_models", token=hf_token)

    # 3. CLIP Vision (necessário para Redux e IP-Adapter)
    print("[3/3] SigLIP CLIP Vision (~1.8GB)...")
    dl("Comfy-Org/sigclip_vision_384", "sigclip_vision_patch14_384.safetensors",
       "/comfyui_models/clip_vision")

    # Commit
    print("\n[PuLID] Commitando no Volume...")
    comfy_volume.commit()

    # Inventário final
    print("\n=== INVENTÁRIO COMPLETO DO VOLUME ===")
    total_gb = 0
    for root, dirs, files in os.walk("/comfyui_models"):
        for f in sorted(files):
            if f.endswith(".safetensors") or f.endswith(".pt") or f.endswith(".pth"):
                full = os.path.join(root, f)
                size_gb = os.path.getsize(full) / (1024**3)
                total_gb += size_gb
                rel = full.replace("/comfyui_models/", "")
                print(f"  ✅ {rel:<60} {size_gb:.2f} GB")

    print(f"\n  TOTAL MODELOS: {total_gb:.2f} GB")
    print("\n✅ Volume pronto para geração com consistência máxima!")
    print("   Pipeline: Referência → PuLID → Flux.1-dev → Cena Final")

@app.local_entrypoint()
def main():
    print("Baixando modelos PuLID + Redux na conta descarganews...")
    download_pulid_and_redux.remote()
