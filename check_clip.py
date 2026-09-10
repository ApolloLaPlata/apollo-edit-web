import modal
app = modal.App('check-qwen-clip')
vol = modal.Volume.from_name('comfyui-models-vol')
@app.function(volumes={'/v': vol})
def run():
  import os
  p = '/v/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors'
  if os.path.exists(p):
    print('SIZE:', os.path.getsize(p))
    with open(p, 'rb') as f: print('HEAD:', f.read(100))
  else:
    print('MISSING!')

@app.local_entrypoint()
def main():
  run.remote()
