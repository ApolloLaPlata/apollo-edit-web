import modal
vol1 = modal.Volume.from_name('comfyui-models-vol')
import modal.app
app = modal.App('check-vols2')
@app.local_entrypoint()
def main():
    print('--- vae ---')
    try:
        for f in vol1.listdir('vae'):
            print(f)
    except Exception as e: print(e)

