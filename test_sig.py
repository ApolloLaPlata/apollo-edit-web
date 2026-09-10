
import modal
app = modal.App("test-sig")
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image)
def get_sig():
    import os
    with open("/comfyui/comfy/ldm/flux/model.py", "r") as f:
        print(f.read())

