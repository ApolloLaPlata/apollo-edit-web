
import modal
import sys
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
from backend.cloud_tools.modal_app import app

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def read_pulid():
    import os
    file_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "forward_orig" in line or "NextDiT" in line:
                    print(f"Line {i+1}: {line.strip()}")
    else:
        print("File not found")

