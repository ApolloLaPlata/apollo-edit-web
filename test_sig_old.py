
import modal
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
app = modal.App("test-sig")
@app.function(image=universal_comfy_image)
def run_command():
    with open("/comfyui/comfy/ldm/flux/model.py", "r") as f:
        c = f.read()
        import re
        m = re.search(r"def forward\(.*?\):", c, re.DOTALL)
        if m:
            print("FOUND MODEL.PY")
            print(m.group(0))
if __name__ == "__main__":
    with app.run():
        run_command.remote()

