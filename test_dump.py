
import modal
app = modal.App("test-dump")
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)

@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def get_dump():
    import os
    hook_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/PulidFluxHook.py"
    if os.path.exists(hook_path):
        print("========== PulidFluxHook.py ==========")
        lines = open(hook_path).readlines()
        for i, line in enumerate(lines):
            if "def pulid_forward" in line:
                print("".join(lines[i:i+15]))
                break
    
    main_path = "/comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll/pulidflux.py"
    if os.path.exists(main_path):
        print("========== pulidflux.py ==========")
        lines = open(main_path).readlines()
        for i, line in enumerate(lines):
            if "pulid_forward" in line:
                print(f"Line {i}: {line.strip()}")

