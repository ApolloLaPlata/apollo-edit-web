import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/engines/minimax_engine.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix huggingface_hub dependency
content = content.replace('"diffusers>=0.30.0", "sentencepiece", "huggingface_hub"', '"diffusers==0.30.0", "sentencepiece", "huggingface_hub<=0.23.2"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Minimax engine deps fixed!")
