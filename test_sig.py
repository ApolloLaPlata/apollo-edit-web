import modal

app = modal.App("test-dir")
vol = modal.Volume.from_name("apollo-models-vol")

@app.function(
    image=modal.Image.debian_slim(python_version="3.10").apt_install("git").pip_install(
        "torch", "torchvision", "transformers", "accelerate", "safetensors",
        "sentencepiece", "protobuf", "numpy", "Pillow", "requests", "soundfile",
        "git+https://github.com/huggingface/diffusers.git"
    ),
    volumes={"/models": vol}
)
def check_sig():
    from diffusers import LTX2Pipeline
    import inspect
    sig = inspect.signature(LTX2Pipeline.__call__)
    for name, param in sig.parameters.items():
        print(f"{name}: {param.default}")

@app.local_entrypoint()
def main():
    check_sig.remote()
