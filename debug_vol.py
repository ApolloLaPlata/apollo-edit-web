import modal
import subprocess
import os

app = modal.App("debug-vol")
vol = modal.Volume.from_name("comfyui-models-vol")

@app.function(volumes={"/vol": vol})
def run_debug():
    return subprocess.check_output("find /vol -type f", shell=True).decode()

@app.local_entrypoint()
def main():
    out = run_debug.remote()
    print("OUTPUT:\n", out)
