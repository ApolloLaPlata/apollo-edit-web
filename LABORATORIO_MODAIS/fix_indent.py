import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/patch_local.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('new_audio_interceptor = """async def', 'new_audio_interceptor = """            async def')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
