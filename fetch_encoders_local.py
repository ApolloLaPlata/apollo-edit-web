import modal
from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
from backend.cloud_tools.engines.universal_engine import app

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    content = engine.fetch_file.remote("/comfyui/comfy/ldm/flux/layers.py")
    with open("encoders_local.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Done!")
