import modal
from backend.cloud_tools.engines.universal_engine import universal_comfy_image as image, app

@app.function(image=image)
def dump_pulid():
    with open("/comfyui/custom_nodes/ComfyUI-PuLID-Flux/pulidflux.py", "r") as f:
        print(f.read())

if __name__ == "__main__":
    with modal.runner.run_stub(app):
        dump_pulid.remote()
