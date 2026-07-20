import modal
import os

app = modal.App("test-dir")
vol = modal.Volume.from_name("apollo-models-vol")

@app.function(volumes={"/models": vol})
def ls():
    path = "/models/huggingface/hub/models--CalamitousFelicitousness--LTX-2.3-Sulphur2-Base-Diffusers"
    if os.path.exists(path):
        print(f"Contents of {path}:")
        for item in os.listdir(path):
            print(f" - {item}")
    else:
        print("Not found")

@app.local_entrypoint()
def main():
    ls.remote()
