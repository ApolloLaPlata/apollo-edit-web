import modal

app = modal.App("ace-step-inspector")

image = modal.Image.debian_slim().apt_install("git").run_commands(
    "git clone https://github.com/ace-step/ACE-Step.git /ACE-Step"
)

@app.function(image=image)
def inspect():
    with open("/ACE-Step/acestep/pipeline_ace_step.py", "r") as f:
        content = f.read()
        # Encontrar a função save_wav_file
        idx = content.find("def save_wav_file")
        print(content[idx:idx+1500])

@app.local_entrypoint()
def main():
    inspect.remote()
