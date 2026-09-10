import modal
app = modal.App('check-qwen')
vol = modal.Volume.from_name('comfyui-models-vol')
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image, volumes={'/v': vol})
def run():
  import os
  os.system('cat /comfyui/comfy_extras/nodes_qwen.py | grep class')

@app.local_entrypoint()
def main():
  run.remote()
