import os
import re

path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\engines\universal_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Clean up previous failed attempts
if 'class BlogUniversalComfyEngine' in text:
    text = text.split('\n@app.cls(\n    gpu="H100"')[0]

if 'class BaseUniversalComfyEngine:' not in text:
    text = text.replace('class UniversalComfyEngine:', 'class BaseUniversalComfyEngine:')
    
app_cls_pattern = r'@app\.cls\([\s\S]*?enable_memory_snapshot=True\n\)'
match = re.search(app_cls_pattern, text)
if match:
    text = text[:match.start()] + text[match.end():]

subclasses = '''

@app.cls(
    gpu="H100",
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume, "/apollo_volume": apollo_volume},
    scaledown_window=60,
    timeout=1200,
    max_containers=5,
    enable_memory_snapshot=True
)
class UniversalComfyEngine(BaseUniversalComfyEngine):
    pass

@app.cls(
    gpu="H100",
    image=universal_comfy_image,
    volumes={"/comfyui_models": comfy_volume, "/apollo_volume": apollo_volume},
    scaledown_window=0,
    timeout=1200,
    max_containers=5,
    enable_memory_snapshot=True
)
class BlogUniversalComfyEngine(BaseUniversalComfyEngine):
    pass
'''

if 'class UniversalComfyEngine(BaseUniversalComfyEngine):' not in text:
    text += subclasses

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Patching done!")
