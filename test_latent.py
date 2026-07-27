import modal
app = modal.App('test-latent')
@app.function(image=modal.Image.debian_slim(python_version='3.10').pip_install('torch'))
def test():
    import torch
    print('test')
@app.local_entrypoint()
def main():
    test.remote()

