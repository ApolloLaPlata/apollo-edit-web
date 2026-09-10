import modal
import os
import glob

app = modal.App("test-dir")
vol = modal.Volume.from_name("apollo-models-vol")

@app.function(volumes={"/models": vol})
def cat_index():
    path = "/models/huggingface/hub/models--CalamitousFelicitousness--LTX-2.3-Sulphur2-Base-Diffusers/snapshots/*/model_index.json"
    files = glob.glob(path)
    if files:
        with open(files[0], "r") as f:
            print(f.read())
    else:
        print("Not found")

@app.local_entrypoint()
def main():
    cat_index.remote()
