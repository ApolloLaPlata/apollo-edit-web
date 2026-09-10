import modal
import os

app = modal.App('check-pulid')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')

@app.function(volumes={'/comfyui_models': comfy_volume})
def check():
    print('Check pulid:')
    if os.path.exists('/comfyui_models/pulid'):
        print(os.listdir('/comfyui_models/pulid'))
    else:
        print('No pulid folder')
    print('Check clip_vision:')
    if os.path.exists('/comfyui_models/clip_vision'):
        print(os.listdir('/comfyui_models/clip_vision'))
    else:
        print('No clip_vision folder')

@app.local_entrypoint()
def main():
    check.remote()

