import modal
app = modal.App("test-out")
@app.function(image=modal.Image.debian_slim(python_version="3.10").pip_install("git+https://github.com/huggingface/diffusers.git"))
def f():
    import diffusers
    try:
        from diffusers.pipelines.ltx.pipeline_ltx2 import LTXVideoPipelineOutput
        print("Output fields:", LTXVideoPipelineOutput.__annotations__)
    except ImportError:
        print("Could not import LTXVideoPipelineOutput")
