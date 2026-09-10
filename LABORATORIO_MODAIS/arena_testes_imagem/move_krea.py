
import modal
app = modal.App("move-krea")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def move_krea():
    import os
    if os.path.exists("/comfyui_models/checkpoints/Krea-2-Raw.safetensors"):
        os.makedirs("/comfyui_models/unet", exist_ok=True)
        os.rename("/comfyui_models/checkpoints/Krea-2-Raw.safetensors", "/comfyui_models/unet/Krea-2-Raw.safetensors")
        comfy_volume.commit()
        print("Moved successfully!")
    else:
        print("File not found in checkpoints!")

