import modal
app = modal.App('dump-f5')
image = modal.Image.debian_slim(python_version='3.11').pip_install('f5-tts')
@app.function(image=image)
def dump():
    import f5_tts.api as api
    import inspect
    print('--- api.py ---')
    print(inspect.getsource(api.F5TTS.__init__))
@app.local_entrypoint()
def main():
    dump.remote()
