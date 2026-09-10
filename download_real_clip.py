import modal
app = modal.App('download-real-qwen-clip')
vol = modal.Volume.from_name('comfyui-models-vol')
@app.function(volumes={'/v': vol}, timeout=3600, image=modal.Image.debian_slim().pip_install('huggingface_hub'))
def run():
  import os
  from huggingface_hub import hf_hub_download
  print('Downloading real qwen clip...')
  os.makedirs('/v/clip', exist_ok=True)
  # Apagar o falso se existir
  if os.path.exists('/v/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors'):
    os.remove('/v/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors')
  hf_hub_download(repo_id='Comfy-Org/Qwen-Image_ComfyUI', filename='split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors', local_dir='/v/clip_temp', local_dir_use_symlinks=False)
  os.rename('/v/clip_temp/split_files/text_encoders/qwen_2.5_vl_7b_fp8_scaled.safetensors', '/v/clip/qwen_2.5_vl_7b_fp8_scaled.safetensors')
  print('Done!')
  vol.commit()

@app.local_entrypoint()
def main():
  run.remote()
