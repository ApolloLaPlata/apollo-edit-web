import modal
import os

app = modal.App('apollo-fix-krea2')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')

@app.function(volumes={'/comfyui_models': comfy_volume})
def move_krea2():
    old_path = '/comfyui_models/checkpoints/Krea-2-Raw.safetensors'
    new_dir = '/comfyui_models/unet'
    new_path = '/comfyui_models/unet/Krea-2-Raw.safetensors'
    os.makedirs(new_dir, exist_ok=True)
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        comfy_volume.commit()
        print(f'Moved {old_path} to {new_path}')
    else:
        print(f'{old_path} not found.')

@app.local_entrypoint()
def main():
    move_krea2.remote()

