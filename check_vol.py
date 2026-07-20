import modal
import os

comfy_volume = modal.Volume.from_name("comfyui-models-vol")
app = modal.App("check-vol")

@app.function(volumes={"/comfyui_models": comfy_volume})
def check():
    path = "/comfyui_models/insightface/models/antelopev2"
    if os.path.exists(path):
        print(f"Contents of {path}:", os.listdir(path))
        print("Is dir?", os.path.isdir(path))
    else:
        print(f"Path {path} does NOT exist!")
        
    path2 = "/comfyui_models/insightface/models"
    if os.path.exists(path2):
        print(f"Contents of {path2}:", os.listdir(path2))

@app.local_entrypoint()
def main():
    check.remote()
