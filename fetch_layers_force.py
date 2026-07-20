import modal
import os
import sys

# Script to bypass cache
app = modal.App("fetch_layers_script")

universal_comfy_image = modal.Image.debian_slim(python_version="3.10")

@app.function(image=universal_comfy_image)
def fetch_layers_now():
    filepath = "/comfyui/comfy/ldm/flux/layers.py"
    with open(filepath, "r") as f:
        return f.read()

@app.local_entrypoint()
def main():
    print("Fetching /comfyui/comfy/ldm/flux/layers.py...")
    content = fetch_layers_now.remote()
    with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/layers_local.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Done!")
