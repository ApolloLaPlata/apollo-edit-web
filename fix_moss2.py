import sys
with open('backend/cloud_tools/engines/moss_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

correct_block = '''    .pip_install(
        "transformers",
        "safetensors==0.6.2",
        "numpy==2.1.0",
        "orjson==3.11.4",
        "tqdm==4.67.1",
        "PyYAML==6.0.3",
        "einops==0.8.1",
        "scipy==1.16.2",
        "librosa==0.11.0",
        "tiktoken==0.12.0",
        "huggingface_hub",
        "fastapi[standard]",
        "accelerate>=0.26.0",
        "torchcodec"
    )
    .run_commands(
        [
            "python -c \\"from huggingface_hub import snapshot_download; print('[BUILD] Baixando Pesos do MOSS-TTS (25GB)...'); snapshot_download(repo_id='OpenMOSS-Team/MOSS-TTS', local_dir_use_symlinks=False)\\""
        ]
    )
)'''

# Replace the broken block
old_block = '''    .pip_install(
        "transformers",
        "safetensors==0.6.2",
        "numpy==2.1.0",
        "orjson==3.11.4",
        ]
    )
)'''
content = content.replace(old_block, correct_block)

with open('backend/cloud_tools/engines/moss_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
