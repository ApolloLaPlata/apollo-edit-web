
import modal
import sys
import os

# Append the current directory so that backend can be found locally
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.cloud_tools.engines.universal_engine import universal_comfy_image

app = modal.App("test-git")
@app.function(image=universal_comfy_image)
def run_command():
    os.system("cd /comfyui/custom_nodes/ComfyUI_PuLID_Flux_ll && git remote -v && git log -n 1")

if __name__ == "__main__":
    with app.run():
        run_command.remote()

