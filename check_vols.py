import modal
import os

app = modal.App('check-vols')
vol1 = modal.Volume.from_name('comfyui-models-vol')
vol2 = modal.Volume.from_name('apollo-models-vol', create_if_missing=True)

@app.local_entrypoint()
def main():
    print('--- comfyui-models-vol ---')
    try:
        for f in vol1.listdir('unet'):
            print(f)
        for f in vol1.listdir('clip'):
            print(f)
    except Exception as e: print(e)
    print('--- apollo-models-vol ---')
    try:
        for f in vol2.listdir('models/diffusion_models'):
            print(f)
        for f in vol2.listdir('models/text_encoders'):
            print(f)
    except Exception as e: print(e)

