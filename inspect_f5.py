import modal
app = modal.App('inspect-f5')
image = modal.Image.debian_slim(python_version='3.11').pip_install('f5-tts')
@app.function(image=image)
def inspect():
    from f5_tts.api import F5TTS
    import inspect
    print(inspect.signature(F5TTS.__init__))
@app.local_entrypoint()
def main():
    inspect.remote()
