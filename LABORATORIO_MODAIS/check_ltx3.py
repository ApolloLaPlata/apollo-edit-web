import modal
app = modal.App()

image = modal.Image.debian_slim().apt_install("git").pip_install("torch", "transformers", "git+https://github.com/huggingface/diffusers.git")

@app.function(image=image)
def check_ltx():
    import inspect
    from diffusers import LTX2Pipeline
    print("LTX2Pipeline signature:")
    sig = inspect.signature(LTX2Pipeline.__call__)
    for name, param in sig.parameters.items():
        print(f"  {name}: {param.default}")
