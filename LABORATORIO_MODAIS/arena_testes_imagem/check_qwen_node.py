
import modal
app = modal.App("check-qwen-node")
comfy_volume = modal.Volume.from_name("comfyui-models-vol", create_if_missing=True)
from backend.cloud_tools.engines.universal_engine import universal_comfy_image
@app.function(image=universal_comfy_image, volumes={"/comfyui_models": comfy_volume})
def check_node():
    import os
    for root, dirs, files in os.walk("/comfyui/custom_nodes"):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                content = open(path, "r", encoding="utf-8", errors="ignore").read()
                if "TextEncodeQwenImageEditPlus" in content:
                    print(f"FOUND IN: {path}")
                    import re
                    match = re.search(r"class TextEncodeQwenImageEditPlus.*?(?=class |$)", content, re.DOTALL)
                    if match:
                        print(match.group(0)[:1000])

