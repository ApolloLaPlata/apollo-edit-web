import modal

app = modal.App("apollolaplata")

@app.function(image=modal.Image.lookup("apollolaplata", "apollo-flux2-universal"))
def get_pulid():
    with open('/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py', 'r') as f:
        return f.read()

@app.local_entrypoint()
def main():
    pulid = get_pulid.remote()
    with open('pulidflux.py', 'w', encoding='utf-8') as f:
        f.write(pulid)
