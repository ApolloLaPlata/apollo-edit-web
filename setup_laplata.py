import modal
import os

app = modal.App("apollo-setup-laplata")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

# Reusing the existing image setup so it has comfyui and the workflow JSON
flux2_comfy_image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git", "libgl1", "libglib2.0-0")
    .pip_install("comfy-cli")
    .add_local_file("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/Comfyui Workflow API/FLUX 2 DEV/image_flux2/image_flux2 .json", "/tmp/workflow.json", copy=True)
    .run_commands([
        "comfy --workspace /comfyui install --nvidia",
    ])
)

@app.function(
    image=flux2_comfy_image,
    volumes={"/comfyui_models": comfy_volume},
    timeout=3600
)
def download_and_move_models():
    import os
    import shutil
    
    print("1. Baixando modelos pelo comfy-cli (direto no container)...")
    os.system("comfy --workspace /comfyui node install-deps --workflow /tmp/workflow.json")
    
    print("2. Movendo os modelos do container para o Volume Persistente...")
    models_dir = "/comfyui/models"
    vol_dir = "/comfyui_models"
    
    for category in ["unet", "vae", "clip", "loras"]:
        src = os.path.join(models_dir, category)
        dst = os.path.join(vol_dir, category)
        if not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)
            
        if os.path.exists(src):
            for file in os.listdir(src):
                src_file = os.path.join(src, file)
                dst_file = os.path.join(dst, file)
                if not os.path.exists(dst_file):
                    print(f"Movendo: {src_file} -> {dst_file}")
                    shutil.copy2(src_file, dst_file)
                else:
                    print(f"Ja existe no volume: {dst_file}")
                    
    print("3. Finalizado! O Volume esta pronto para ser usado no apollolaplata.")

if __name__ == "__main__":
    download_and_move_models.remote()
