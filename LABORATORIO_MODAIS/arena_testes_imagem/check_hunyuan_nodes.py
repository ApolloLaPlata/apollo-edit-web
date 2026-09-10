import modal
app = modal.App("check-hunyuan-nodes")
@app.local_entrypoint()
def main():
    check.remote()

@app.function(image=modal.Image.debian_slim().apt_install("git").run_commands("git clone https://github.com/comfyanonymous/ComfyUI /comfyui"))
def check():
    with open("/comfyui/nodes.py") as f:
        code = f.read()
    print("EmptyHunyuanLatentVideo:", "EmptyHunyuanLatentVideo" in code)
    print("hunyuan_video:", "hunyuan_video" in code)
