import modal
import os
import sys

app = modal.App("temp-check-comfy")

image = modal.Image.debian_slim(python_version="3.10").pip_install("comfy-cli==1.2.7").run_commands(["comfy --workspace /comfyui install --nvidia"])

@app.function(image=image)
def get_file():
    with open("/comfyui/comfy/model_management.py", "r") as f:
        content = f.read()
        return content

if __name__ == "__main__":
    with modal.enable_output():
        with app.run():
            print(get_file.remote())
