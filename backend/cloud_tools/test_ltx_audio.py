import modal
import modal
apollo_image = modal.Image.debian_slim().apt_install("ffmpeg", "git").pip_install("torch", "torchaudio", "git+https://github.com/huggingface/diffusers.git", "transformers", "accelerate", "scipy")
apollo_volume = modal.Volume.from_name("apollo-models-vol", create_if_missing=True)

app = modal.App()

@app.function(
    image=apollo_image,
    volumes={"/models": apollo_volume},
    gpu="H100"
)
def test_audio():
    from diffusers import LTX2Pipeline
    import torch
    cache_dir = "/models/huggingface/hub/models--diffusers--LTX-2.3-Diffusers"
    print("Loading LTX2Pipeline...")
    pipe = LTX2Pipeline.from_pretrained(cache_dir, torch_dtype=torch.bfloat16, local_files_only=True)
    pipe.to("cuda")
    print("Running pipeline...")
    out = pipe(prompt="A dog barking", num_inference_steps=1, num_frames=9, return_dict=True)
    
    if isinstance(out, dict):
        print("Dict keys:", out.keys())
    else:
        print("Object attributes:", dir(out))
        if hasattr(out, "audios"):
            print("audios is None?", out.audios is None)
        if hasattr(out, "audio"):
            print("audio is None?", out.audio is None)
