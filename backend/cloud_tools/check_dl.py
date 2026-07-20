import modal
import os

app = modal.App("check-dl")
comfy_volume = modal.Volume.from_name("apollo-comfy-volume", create_if_missing=True)

@app.function(volumes={"/comfyui": comfy_volume})
def check():
    def get_size(path):
        if os.path.exists(path):
            return f"{os.path.getsize(path) / (1024*1024):.2f} MB"
        return "N/A"
    print("KLEIN:", get_size("/comfyui/models/diffusion_models/flux-2-klein-base-4b-fp8.safetensors"))
    print("QWEN:", get_size("/comfyui/models/text_encoders/qwen_3_4b.safetensors"))
    print("VAE:", get_size("/comfyui/models/vae/full_encoder_small_decoder.safetensors"))

@app.local_entrypoint()
def main():
    check.remote()
