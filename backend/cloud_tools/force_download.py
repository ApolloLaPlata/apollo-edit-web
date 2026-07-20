import modal

app = modal.App("force-download-klein")
comfy_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)
img = modal.Image.debian_slim().apt_install("git").pip_install("comfy-cli")

@app.function(image=img, volumes={"/comfyui": comfy_volume}, timeout=3600)
def download_models():
    import os
    print("Baixando FLUX KLEIN...")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.2-klein-base-4b-fp8/resolve/main/flux-2-klein-base-4b-fp8.safetensors --relative-path models/diffusion_models")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/ModelTrainingSpace/qwen_3_4b/resolve/main/qwen_3_4b.safetensors --relative-path models/text_encoders")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/black-forest-labs/FLUX.2-small-decoder/resolve/main/full_encoder_small_decoder.safetensors --relative-path models/vae")
    print("Download completo!")

@app.local_entrypoint()
def main():
    download_models.remote()
