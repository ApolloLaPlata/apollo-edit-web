import modal
app = modal.App('dump-clip')
vol = modal.Volume.from_name('comfyui-models-vol')
@app.function(volumes={'/v': vol})
def run():
  import json, struct
  with open('/v/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors', 'rb') as f:
    length = struct.unpack('<Q', f.read(8))[0]
    header = json.loads(f.read(length).decode('utf-8'))
  print(list(header.keys())[:50])

@app.local_entrypoint()
def main():
  run.remote()
