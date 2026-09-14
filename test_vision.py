import modal
import base64

# read an image
with open("C:/Users/v5est/.gemini/antigravity/brain/a22deae7-7753-458c-a40d-92e685f8af3e/.user_uploaded/media_1789084866148.png", "rb") as f:
    img_data = base64.b64encode(f.read()).decode('utf-8')

import sys
sys.path.append('E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB')
from backend.cloud_tools.engines.vision_engine import FlorenceVisionEngine

cls = modal.Cls.from_name("apollo-vision-engine", "FlorenceVisionEngine")
print(cls().analyze_image.remote(img_data))
