import modal
app = modal.App("apollo-minimax-engine")
volume = modal.Volume.from_name("apollo-models", create_if_missing=True)
image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.11").pip_install("torch", "transformers", "diffusers>=0.30.0", "huggingface_hub")

@app.function(image=image, volumes={"/models": volume})
def inspect_minimax():
    import inspect
    from diffusers import ModularPipeline
    import diffusers
    print("Diffusers version:", diffusers.__version__)
    try:
        from diffusers.modular_pipelines.minimax_music3.encoders import check_inputs
        print("Source:", inspect.getsource(check_inputs))
    except Exception as e:
        print("Error:", e)
