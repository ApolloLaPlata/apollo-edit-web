import modal
app = modal.App('read-att')
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image, mounts=[modal.Mount.from_local_python_packages('backend')])
def run():
  import os
  os.system('cat /comfyui/comfy/ldm/modules/attention.py | grep gqa')

@app.local_entrypoint()
def main():
  run.remote()
