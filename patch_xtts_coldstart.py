# -*- coding: utf-8 -*-
import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/xtts_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Substituir a definição da imagem para incluir o download do modelo
old_image = r'''xtts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch<2.6.0",
        "torchaudio<2.6.0",
        "TTS==0.22.0",
        "soundfile",
        "fastapi[standard]",
        "numpy<2.0.0", # TTS pode ter problemas com numpy 2.0
        "transformers<4.35.0" # XTTSv2 (TTS 0.22) quebra se usar o Transformers atual
    )
)'''

new_image = r'''def download_xtts():
    import os
    os.environ["COQUI_TOS_AGREED"] = "1"
    from TTS.api import TTS
    # Fazer o download do modelo para dentro da camada da imagem Docker (bakear o modelo)
    TTS("tts_models/multilingual/multi-dataset/xtts_v2")

xtts_image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install(
        "torch<2.6.0",
        "torchaudio<2.6.0",
        "TTS==0.22.0",
        "soundfile",
        "fastapi[standard]",
        "numpy<2.0.0",
        "transformers<4.35.0"
    )
    .run_function(download_xtts)
)'''

text = text.replace(old_image, new_image)

# Mudar de T4 para L4 para acelerar a execução de 9s para ~3s
text = text.replace('gpu="T4"', 'gpu="L4"')

# Remover o volume pois o modelo já estará bakeado na imagem (Volumes deixam o cold start mais lento)
text = text.replace(', volumes={"/root/.local/share/tts": xtts_cache}', '')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("xtts_engine.py otimizado para Cold Start ZERO e Inferência L4!")
