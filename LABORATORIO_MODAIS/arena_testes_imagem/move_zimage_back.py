import modal
import shutil
import os

app = modal.App("move-zimage-back")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.local_entrypoint()
def main():
    move.remote()

@app.function(volumes={"/vol": vol})
def move():
    source = "/vol/checkpoints/redzibDX1.safetensors"
    dest = "/vol/unet/redzibDX1.safetensors"
    if os.path.exists(source):
        shutil.move(source, dest)
        vol.commit()
        print("Movido Z-Image de volta para unet!")
    else:
        print("Nao encontrado!")
