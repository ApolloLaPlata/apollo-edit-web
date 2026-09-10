import modal

app = modal.App('apollo-download-krea2-raw')
comfy_volume = modal.Volume.from_name('comfyui-models-vol', create_if_missing=True)
image = modal.Image.debian_slim().pip_install('huggingface_hub', 'hf_transfer')

@app.function(
    image=image,
    volumes={'/comfyui_models': comfy_volume},
    timeout=3600
)
def download_krea2_raw():
    import os
    os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '1'
    from huggingface_hub import hf_hub_download
    
    dest_dir = '/comfyui_models/checkpoints'
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, 'Krea-2-Raw.safetensors')
    
    print('Iniciando download do Krea 2 Raw (Base) da HuggingFace...')
    
    if os.path.exists(dest_file):
        print('Arquivo ja existe. Tamanho:', os.path.getsize(dest_file))
        return
        
    try:
        downloaded_path = hf_hub_download(
            repo_id='krea/Krea-2-Raw',
            filename='raw.safetensors',
            local_dir=dest_dir,
            local_dir_use_symlinks=False,
            token='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'
        )
        if downloaded_path != dest_file:
            os.rename(downloaded_path, dest_file)
        print('\nDownload concluido com sucesso!')
        print(f'Arquivo salvo em: {dest_file}')
        comfy_volume.commit()
    except Exception as e:
        print(f'Erro no download: {e}')

@app.local_entrypoint()
def main():
    print('Enviando tarefa de download Krea-2-Raw para a Modal...')
    download_krea2_raw.remote()
    print('Tarefa finalizada.')

