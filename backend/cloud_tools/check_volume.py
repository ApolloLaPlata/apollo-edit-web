import modal
import os

app = modal.App('check-volume')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')

@app.function(volumes={'/comfyui_models/': comfy_volume})
def check_files():
    os.system('ls -lhR /comfyui_models/')

@app.local_entrypoint()
def main():
    check_files.remote()
