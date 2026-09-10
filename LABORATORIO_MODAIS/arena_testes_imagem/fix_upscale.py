import modal
import shutil
import os
app = modal.App("fix-upscale")
vol = modal.Volume.from_name("comfyui-models-vol")
@app.function(volumes={"/comfyui_models": vol})
def fix():
    # Because we don't have write access to /comfyui (it's inside the image, wait, is it in the image?)
    # /comfyui is in the image, we can just write to /comfyui_models and update the yaml
    pass
@app.local_entrypoint()
def main():
    fix.remote()
