import json
import base64
import time
from PIL import Image
import io
import os

from backend.cloud_tools.engines.universal_engine import UniversalComfyEngine
from modal import App

app = App("test-upscale")

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    print("Iniciando upscale...")
    
    # Generate a dummy 1280x720 image to ensure the input is 1280x720
    dummy_img = Image.new("RGB", (1280, 720), color="blue")
    buf = io.BytesIO()
    dummy_img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        
    with open(r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\flux_upscale_ultrasharp.json", "r") as f:
        upscale_json = f.read()

    t0 = time.time()
    res = engine.generate.remote(
        workflow_json_string=upscale_json,
        prompt="A highly detailed testing image",
        input_image_b64=img_b64,
        is_upscale=True,
        denoise=0.25
    )
    t1 = time.time()
    
    print(f"Time taken: {t1 - t0}s")
    if res.get("status") == "success":
        img = Image.open(io.BytesIO(base64.b64decode(res["image_base64"])))
        print(f"Result size: {img.size}")
    else:
        print(res)
