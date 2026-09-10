
import modal
app = modal.App("ls-ckpt")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def ls_ckpt():
    import os
    print(os.listdir("/comfyui_models/checkpoints/"))

