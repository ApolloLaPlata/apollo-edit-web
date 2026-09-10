import modal

app = modal.App("apollo-voice-downloader")

image = modal.Image.debian_slim(python_version="3.10").pip_install("modelscope")
vol = modal.Volume.from_name("apollo-voice-models", create_if_missing=True)

@app.function(image=image, volumes={"/models": vol}, timeout=10800)
def download_model():
    import os
    from modelscope import snapshot_download
    print("Iniciando download seguro para o volume permanente...")
    model_dir = snapshot_download('iic/CosyVoice2-0.5B', cache_dir='/models/modelscope_cache')
    print(f"Download concluído e salvo em: {model_dir}")

@app.local_entrypoint()
def main():
    print("Executando job de download do CosyVoice2...")
    download_model.remote()
    print("Sucesso!")
