import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/cloud_tools/apollo_modal_engine.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"async def stream_result\(\):.*?(?=except Exception as e:\n        return \{\"status\": \"error\", \"message\": f\"Erro de roteamento Audio Lab)"
# wait, the catch for Audio Lab might not be exactly that.
