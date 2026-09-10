import modal
app = modal.App("check-hunyuan-nodes-3")
@app.local_entrypoint()
def main():
    check.remote()

@app.function(image=modal.Image.debian_slim().apt_install("git").run_commands("git clone https://github.com/comfyanonymous/ComfyUI /comfyui"))
def check():
    with open("/comfyui/comfy_extras/nodes_hunyuan.py") as f:
        print(f.read())
