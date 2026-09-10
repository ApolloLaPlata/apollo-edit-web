import re

with open("backend/cloud_tools/engines/vision_engine.py", "r", encoding="utf-8") as f:
    vision = f.read()

# Make sure analyze_image moves model to CUDA if available
move_code = """        import torch
        if torch.cuda.is_available() and self.model.device.type != "cuda":
            print("[VisionEngine] Movendo modelo do CPU para CUDA (pos-snapshot)...")
            self.model = self.model.to("cuda")
            
        from PIL import Image"""

vision = re.sub(r"        from PIL import Image", move_code, vision)

with open("backend/cloud_tools/engines/vision_engine.py", "w", encoding="utf-8") as f:
    f.write(vision)

print("Vision patch applied!")
