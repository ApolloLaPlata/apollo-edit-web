import modal
app = modal.App("read-quant-ops")

@app.local_entrypoint()
def main():
    pass

@app.function(image=modal.Image.lookup("universal_comfy_image", create_if_missing=False))
def read_file():
    with open("/comfyui/comfy/quant_ops.py", "r") as f:
        print(f.read())

if __name__ == "__main__":
    with app.run():
        read_file.remote()
