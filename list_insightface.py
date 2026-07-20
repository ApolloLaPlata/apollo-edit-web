import modal
import os
app = modal.App("list_insight")
comfy_volume = modal.Volume.from_name("comfyui-models-vol")

@app.function(volumes={"/comfyui_models": comfy_volume})
def list_insightface():
    import subprocess
    result = subprocess.run("find /comfyui_models/insightface", shell=True, capture_output=True, text=True)
    print(result.stdout)

@app.local_entrypoint()
def main():
    list_insightface.remote()
