import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cloud_tools.engines.cosyvoice_engine import app, cosy_image

@app.local_entrypoint()
def main():
    print(inspect_sig.remote())

@app.function(image=cosy_image)
def inspect_sig():
    import sys
    sys.path.insert(0, "/workspace/CosyVoice")
    from cosyvoice.cli.cosyvoice import CosyVoice2
    import inspect
    methods = inspect.getmembers(CosyVoice2, predicate=inspect.isfunction)
    
    sigs = {}
    for m in methods:
        if m[0].startswith("inference_"):
            sigs[m[0]] = str(inspect.signature(m[1]))
    return sigs
