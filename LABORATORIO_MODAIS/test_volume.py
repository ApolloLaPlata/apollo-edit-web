import modal
import os

vol = modal.Volume.from_name('apollo-models-vol', create_if_missing=True)
app = modal.App('apollo-test-volume')

@app.function(volumes={'/models': vol})
def list_files():
    path = '/models/huggingface/hub'
    print(f'--- Contents of {path} ---')
    if os.path.exists(path):
        for item in os.listdir(path):
            print(f'  - {item}')
    else:
        print('PATH NOT FOUND')

@app.local_entrypoint()
def main():
    list_files.remote()
