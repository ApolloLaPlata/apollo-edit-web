import modal
import shutil
import os

app = modal.App("move-vol")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    move.remote()

@app.function(volumes={"/vol": vol})
def move():
    source = "/vol/unet/redzibDX1.safetensors"
    dest = "/vol/checkpoints/redzibDX1.safetensors"
    if os.path.exists(source):
        shutil.move(source, dest)
        vol.commit()
        print("Movido Z-Image para checkpoints!")
    else:
        print("Nao encontrado!")
