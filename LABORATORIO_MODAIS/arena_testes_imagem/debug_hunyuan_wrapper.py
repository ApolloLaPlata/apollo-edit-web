import modal
import os
import sys

from backend.cloud_tools.engines.universal_engine import universal_comfy_image
from backend.cloud_tools.modal_app import app

vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    debug_import.remote()

@app.function(
    image=universal_comfy_image,
    volumes={"/comfyui_models": vol}
)
def debug_import():
    import traceback
    sys.path.append("/comfyui")
    sys.path.append("/comfyui/custom_nodes")
    try:
        import nodes
        import importlib
        importlib.import_module("ComfyUI-HunyuanVideoWrapper.__init__")
        print("IMPORT SUCCEEDED!")
    except Exception as e:
        print("IMPORT FAILED!")
        traceback.print_exc()
