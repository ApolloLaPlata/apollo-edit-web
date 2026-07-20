import modal
import os
import sys
import json
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from engines.universal_engine import UniversalComfyEngine, app

def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

@app.local_entrypoint()
def main():
    engine = UniversalComfyEngine()
    print("Testing UniversalComfyEngine...")
    
    workflow_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\Comfyui Workflow API\FLUX.2 [KLEIN] 4B\FLUX.2 [KLEIN] 4B Edição de imagem\workflow_multipass_klein.json"
    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_json_string = f.read()

    # Load 2 images as example
    img1_path = r"C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\media__1783202530330.jpg"
    img2_path = r"C:\Users\v5est\.gemini\antigravity\brain\1a81570a-dcb0-4985-9cbf-0bca86071582\media__1783202547761.jpg"
    
    b64_1 = image_to_base64(img1_path)
    b64_2 = image_to_base64(img2_path)
    
    script = {
        "workflow_json_string": workflow_json_string,
        "etapas": [
            {
                "prompt": "First pass modification, blending character 1 into the scene",
                "image_b64": b64_1
            },
            {
                "prompt": "Second pass modification, blending character 2 into the scene seamlessly",
                "image_b64": b64_2
            }
        ]
    }
    
    print("Invoking remote multi_pass_generation...")
    result = engine.multi_pass_generation.remote(script)
    
    if result.get("status") == "success":
        print(f"Success! Render time: {result.get('render_time_seconds')}s")
        final_img = result.get("image_base64")
        out_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\resultado_multipass_direto.png"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(final_img))
        print(f"Saved to {out_path}")
    else:
        print("Error:")
        print(result)

if __name__ == "__main__":
    pass
