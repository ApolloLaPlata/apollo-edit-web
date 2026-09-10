import modal
import os
app = modal.App("check-upscale")
vol = modal.Volume.from_name("comfyui-models-vol")
@app.local_entrypoint()
def main(): check.remote()
@app.function(volumes={"/comfyui_models": vol})
def check():
    path = "/comfyui_models/upscale_models"
    if os.path.exists(path):
        print("Upscale models:", os.listdir(path))
    else:
        print("Path does not exist")
