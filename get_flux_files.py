import modal

app = modal.App("apollolaplata")

@app.function(image=modal.Image.lookup("apollolaplata", "apollo-flux2-universal"))
def get_files():
    with open('/comfyui/comfy/ldm/flux/model.py', 'r') as f:
        model = f.read()
    with open('/comfyui/comfy/ldm/flux/layers.py', 'r') as f:
        layers = f.read()
    return model, layers

@app.local_entrypoint()
def main():
    model, layers = get_files.remote()
    with open('modal_model.py', 'w', encoding='utf-8') as f:
        f.write(model)
    with open('modal_layers.py', 'w', encoding='utf-8') as f:
        f.write(layers)
    print("Files extracted.")
