import modal
app = modal.App('test-qwen-isolated')
from backend.cloud_tools.engines.qwen_image_engine import QwenImageEngine
@app.local_entrypoint()
def main():
  engine = QwenImageEngine()
  res = engine.generate.remote(prompt='A cinematic ultra-realistic 4k shot of a futuristic cyberpunk city with flying cars')
  print(res)
  if 'image_base64' in res:
    import base64
    with open('teste_qwen_ROXINGO.jpg', 'wb') as f:
      f.write(base64.b64decode(res['image_base64']))
    print('Saved to teste_qwen_ROXINGO.jpg')
