import modal
app = modal.App('grep-qwen')
@app.function(image=modal.Image.debian_slim().pip_install('requests'))
def run():
  import os
  os.system('cat /comfyui/comfy_extras/nodes_qwen.py | grep class')

@app.local_entrypoint()
def main():
  run.remote()
