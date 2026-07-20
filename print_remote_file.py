import modal
from backend.cloud_tools.engines.universal_engine import universal_comfy_image as image

app = modal.App("apollo-print")

@app.function(image=image)
def print_file():
    with open("/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py", "r") as f:
        return f.read()

@app.local_entrypoint()
def main():
    print(print_file.remote())
