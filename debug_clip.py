import modal
app = modal.App('debug-comfy')
from backend.cloud_tools.engines.qwen_image_engine import orchestrator_image
vol = modal.Volume.from_name('comfyui-models-vol')
@app.function(image=orchestrator_image, volumes={'/comfyui_models': vol})
def run():
  import os
  os.system('cat /comfyui/comfy/sd.py | grep qwen_image')
  os.system('cat /comfyui/comfy/text_encoders/qwen.py | head -n 20')

@app.local_entrypoint()
def main():
  run.remote()
