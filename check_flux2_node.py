import modal
import os
import subprocess
app = modal.App('check-flux2-node')
from backend.cloud_tools.engines.universal_engine import comfy_image
@app.function(image=comfy_image)
def run_grep():
    try:
        result = subprocess.run(['grep', '-r', 'EmptyFlux2LatentImage', '/comfyui'], capture_output=True, text=True)
        print('--- GREP RESULTS ---')
        print(result.stdout)
    except Exception as e: print(e)
@app.local_entrypoint()
def main():
    run_grep.remote()

