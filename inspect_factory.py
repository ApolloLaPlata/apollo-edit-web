import modal

app = modal.App("inspect-factory")
image = modal.Image.from_registry("nvidia/cuda:12.1.1-devel-ubuntu22.04", add_python="3.10") \
    .apt_install("git") \
    .pip_install("torch", "torchaudio") \
    .run_commands("git clone https://github.com/Stability-AI/stable-audio-tools.git /stable-audio-tools") \
    .run_commands("cd /stable-audio-tools && pip install -e .")

@app.function(image=image)
def inspect():
    import stable_audio_tools.models.factory as factory
    print(dir(factory))

@app.local_entrypoint()
def main():
    inspect.remote()