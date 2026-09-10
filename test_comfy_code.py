
import modal
app = modal.App("test-comfy")
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image)
def get_comfy_code():
    with open("/comfyui/comfy/ldm/flux/model.py", "r") as f:
        c = f.read()
        import re
        m = re.search(r"def forward\(.*?\):", c, re.DOTALL)
        if m:
            print("FOUND MODEL.PY")
            print(m.group(0))
        else:
            print("NOT FOUND IN MODEL.PY")
            

