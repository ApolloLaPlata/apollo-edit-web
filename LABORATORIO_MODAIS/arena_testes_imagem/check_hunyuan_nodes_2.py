import modal
app = modal.App("check-hunyuan-nodes-2")
@app.local_entrypoint()
def main():
    check.remote()

@app.function(image=modal.Image.debian_slim().apt_install("git").run_commands("git clone https://github.com/comfyanonymous/ComfyUI /comfyui"))
def check():
    with open("/comfyui/nodes.py") as f:
        lines = f.readlines()
    for line in lines:
        if "EmptyLatent" in line or "Hunyuan" in line or "hunyuan" in line:
            print(line.strip())
