import modal
from backend.cloud_tools.engines.fish_engine import fish_image

app = modal.App('inspect-fish')

@app.function(image=fish_image)
def inspect():
    import pkgutil
    import importlib
    import fish_speech
    print('MODULES IN FISH_SPEECH:', [m.name for m in pkgutil.iter_modules(fish_speech.__path__)])
    try:
        import tools
        print('MODULES IN TOOLS:', [m.name for m in pkgutil.iter_modules(tools.__path__)])
    except:
        print('NO TOOLS MODULE')

@app.local_entrypoint()
def main():
    inspect.remote()

