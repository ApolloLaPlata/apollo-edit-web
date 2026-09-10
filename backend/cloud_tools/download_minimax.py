import modal
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append('/root')
sys.path.append('/pkg')
sys.path.append('/')

from backend.cloud_tools.engines.universal_engine import universal_comfy_image, comfy_volume
from backend.cloud_tools.modal_app import app

@app.function(
    image=universal_comfy_image,
    volumes={'/comfyui_models': comfy_volume},
    secrets=[modal.Secret.from_name('huggingface-secret')],
    timeout=3600
)
def download_minimax():
    print('[Universal Downloader] Baixando MiniMax H3...')
    from huggingface_hub import snapshot_download
    snapshot_download(
        repo_id='MiniMaxAI/MiniMax-H3',
        local_dir='/comfyui_models/checkpoints/MiniMax-H3',
        local_dir_use_symlinks=False,
    )
    print('[Universal Downloader] Downloads finalizados!')
    comfy_volume.commit()
