
import modal
app = modal.App("read-pulid")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
@app.function(image=modal.Image.debian_slim().pip_install("requests"), volumes={"/comfyui_models": comfy_volume})
def do_read():
    import os
    print(os.listdir("/comfyui_models"))

