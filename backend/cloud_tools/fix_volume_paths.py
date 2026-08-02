import modal
import os
import shutil

app = modal.App('fix-volume-paths')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')
img = modal.Image.debian_slim()

@app.function(image=img, volumes={'/comfyui_models': comfy_volume})
def fix_paths():
    print('Moving files...')
    
    os.makedirs('/comfyui_models/unet', exist_ok=True)
    os.makedirs('/comfyui_models/clip', exist_ok=True)
    
    if os.path.exists('/comfyui_models/diffusion_models/flux-2-klein-base-4b-fp8.safetensors'):
        shutil.move('/comfyui_models/diffusion_models/flux-2-klein-base-4b-fp8.safetensors', '/comfyui_models/unet/flux-2-klein-base-4b-fp8.safetensors')
        print('Moved flux-2-klein')
        
    if os.path.exists('/comfyui_models/text_encoders/qwen_3_4b.safetensors'):
        shutil.move('/comfyui_models/text_encoders/qwen_3_4b.safetensors', '/comfyui_models/clip/qwen_3_4b.safetensors')
        print('Moved qwen')

    # Commit changes to the volume
    print('All moved!')

@app.local_entrypoint()
def main():
    fix_paths.remote()
