import modal
import os
import urllib.request

app = modal.App(name="apollo-download-ultrasharp")
apollo_volume = modal.Volume.from_name("apollo-comfy-volume")

@app.function(volumes={"/apollo_volume": apollo_volume})
def download():
    path = "/apollo_volume/models/upscale_models"
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, "4x-UltraSharp.pth")
    if not os.path.exists(file_path):
        print(f"Baixando 4x-UltraSharp.pth...")
        url = "https://huggingface.co/uwg/upscaler/resolve/main/ESRGAN/4x-UltraSharp.pth"
        urllib.request.urlretrieve(url, file_path)
        print("Download concluido!")
    else:
        print("4x-UltraSharp.pth ja existe!")
    apollo_volume.commit()

@app.local_entrypoint()
def main():
    download.remote()
