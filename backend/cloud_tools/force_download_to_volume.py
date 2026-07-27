import modal
import os

app = modal.App('force-download-to-volume')
comfy_volume = modal.Volume.from_name('comfyui-models-vol')
img = modal.Image.debian_slim().apt_install('wget')

@app.function(image=img, volumes={'/comfyui_models': comfy_volume}, timeout=3600, secrets=[modal.Secret.from_name('huggingface-secret')])
def download_models():
    print('Downloading directly to volume...')
    os.makedirs('/comfyui_models/vae', exist_ok=True)
    os.makedirs('/comfyui_models/pulid', exist_ok=True)
    os.makedirs('/comfyui_models/diffusion_models', exist_ok=True)
    os.makedirs('/comfyui_models/text_encoders', exist_ok=True)

    print('Downloading ae.safetensors...')
    os.system('wget --header="Authorization: Bearer $HF_TOKEN" -nc -O /comfyui_models/vae/ae.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors')

    print('Downloading pulid...')
    os.system('wget -nc -O /comfyui_models/pulid/pulid_flux_v0.9.0.safetensors https://huggingface.co/guozinan/PuLID/resolve/main/pulid_flux_v0.9.0.safetensors')

    print('Downloading flux-2-klein...')
    os.system('wget -nc -O /comfyui_models/diffusion_models/flux-2-klein-base-4b-fp8.safetensors https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8/resolve/main/flux-2-klein-base-4b-fp8.safetensors')

    print('Downloading qwen...')
    os.system('wget -nc -O /comfyui_models/text_encoders/qwen_3_4b.safetensors https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors')

    print('Downloading full_encoder...')
    os.system('wget -nc -O /comfyui_models/vae/full_encoder_small_decoder.safetensors https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors')

    print('All downloads finished!')

@app.local_entrypoint()
def main():
    download_models.remote()
