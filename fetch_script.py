import modal
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
from backend.cloud_tools.engines.universal_engine import app

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    print(engine.fetch_file.remote("/comfyui/comfy/ldm/flux/layers.py"))
