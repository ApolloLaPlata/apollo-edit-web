import modal

app = modal.App("force-download-qwen")
comfy_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)
img = modal.Image.debian_slim().apt_install("git").pip_install("comfy-cli")

@app.function(image=img, volumes={"/comfyui": comfy_volume}, timeout=3600)
def download_models():
    import os
    print("Baixando QWEN 3.4B text encoder...")
    os.system("comfy --workspace /comfyui model download --url https://huggingface.co/Comfy-Org/z_image_turbo/resolve/main/split_files/text_encoders/qwen_3_4b.safetensors --relative-path models/text_encoders")
    print("Download completo!")

@app.local_entrypoint()
def main():
    download_models.remote()
