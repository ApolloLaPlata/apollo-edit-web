import modal
import os

app = modal.App("ls-vol")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    ls.remote()

@app.function(volumes={"/vol": vol})
def ls():
    print("CHECKPOINTS:", os.listdir("/vol/checkpoints"))
    print("UNET:", os.listdir("/vol/unet"))
