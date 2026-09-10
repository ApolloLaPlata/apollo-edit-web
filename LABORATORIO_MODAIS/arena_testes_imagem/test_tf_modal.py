import modal
app = modal.App('test-tf')
image = modal.Image.debian_slim().pip_install('transformers==4.45.2', 'torch', 'accelerate')
@app.local_entrypoint()
def main():
    run.remote()
@app.function(image=image)
def run():
    import transformers
    print('TRANSFORMERS VERSION:', transformers.__version__)
    try:
        from transformers.cache_utils import OffloadedCache
        print('OffloadedCache FOUND')
    except Exception as e:
        print('OffloadedCache MISSING', str(e))
    print('Success')
