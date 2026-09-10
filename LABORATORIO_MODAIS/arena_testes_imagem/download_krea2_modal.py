import modal

app = modal.App('apollo-download-krea2')
comfy_volume = modal.Volume.from_name('comfyui-models-vol', create_if_missing=True)

@app.function(
    volumes={'/comfyui_models': comfy_volume},
    timeout=3600
)
def download_krea2():
    import urllib.request
    import os
    
    url = 'https://huggingface.co/krea/Krea-2-Turbo/resolve/main/turbo.safetensors?download=true'
    dest_path = '/comfyui_models/checkpoints/Krea-2-Turbo.safetensors'
    
    print(f'Iniciando download do Krea 2 Turbo para {dest_path}...')
    
    if os.path.exists(dest_path):
        print('Arquivo ja existe. Tamanho:', os.path.getsize(dest_path))
        return
        
    def reporthook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        if count % 10000 == 0:
            print(f'Baixando... {percent}% concluido', end='\r')
            
    urllib.request.urlretrieve(url, dest_path, reporthook=reporthook)
    print('\nDownload concluido com sucesso!')
    print(f'Arquivo salvo em: {dest_path}')
    print(f'Tamanho: {os.path.getsize(dest_path) / (1024*1024*1024):.2f} GB')
    comfy_volume.commit()

@app.local_entrypoint()
def main():
    print('Enviando tarefa de download para a Modal...')
    download_krea2.remote()
    print('Tarefa finalizada.')

