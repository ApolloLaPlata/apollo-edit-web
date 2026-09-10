
import re

path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py"
with open(path, "r", encoding="utf-8") as f:
    code = f.read()

# Add the import at the top
if "import backend.cloud_tools.engines.qwen_image_engine" not in code:
    code = code.replace("import backend.cloud_tools.engines.openvoice_engine", "import backend.cloud_tools.engines.openvoice_engine\nimport backend.cloud_tools.engines.qwen_image_engine")
    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
print("Added import to apollo_modal_engine.py")

