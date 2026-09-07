import modal
app = modal.App('move-qwen-model')
vol = modal.Volume.from_name('comfyui-models-vol')
@app.function(volumes={'/v': vol})
def run():
  import os
  if os.path.exists('/v/checkpoints/qwen_image_edit_2511_bf16.safetensors'):
    os.makedirs('/v/unet', exist_ok=True)
    os.rename('/v/checkpoints/qwen_image_edit_2511_bf16.safetensors', '/v/unet/qwen_image_edit_2511_bf16.safetensors')
    print('Movido checkpoints -> unet!')
  elif os.path.exists('/v/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors'):
    os.makedirs('/v/unet', exist_ok=True)
    os.rename('/v/split_files/diffusion_models/qwen_image_edit_2511_bf16.safetensors', '/v/unet/qwen_image_edit_2511_bf16.safetensors')
    print('Movido split_files -> unet!')
  else:
    print('Nao encontrado!')
  vol.commit()

@app.local_entrypoint()
def main():
  run.remote()
