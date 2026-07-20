import modal
import subprocess

app = modal.App("comfyui-help")

image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10").apt_install("git").pip_install("comfy-cli").run_commands(["comfy --workspace /comfyui install --nvidia"])

@app.function(image=image)
def get_help():
    out = subprocess.check_output(['python', 'main.py', '--help'], cwd='/comfyui', text=True)
    print(out)
    return out

@app.local_entrypoint()
def main():
    get_help.remote()
