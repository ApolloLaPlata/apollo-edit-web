import modal
from backend.cloud_tools.engines.universal_engine import universal_comfy_image

app = modal.App("debug-pulid")

@app.function(image=universal_comfy_image)
def cat_pulid():
    with open('/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py', 'r') as f:
        print(f.read())
