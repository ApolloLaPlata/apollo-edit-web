import modal
import sys
import traceback
import subprocess
import os

comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
universal_comfy_image = modal.Image.debian_slim().pip_install("torch").run_commands(
    "git clone https://github.com/comfyanonymous/ComfyUI.git /comfyui"
)

app = modal.App("debug-hunyuan2")

@app.local_entrypoint()
def main():
    run.remote()

@app.function(
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume}
)
def run():
    subprocess.run(["git", "clone", "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper.git", "/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper"])
    subprocess.run(["pip", "install", "-r", "/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper/requirements.txt"])
    
    sys.path.append('/comfyui/custom_nodes/ComfyUI-HunyuanVideoWrapper')
    sys.path.append('/comfyui')
    
    try:
        import nodes
        print("IMPORT FUNCIONOU!")
    except Exception as e:
        traceback.print_exc()
