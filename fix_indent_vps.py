import re

file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the indentation of async def audio_interceptor
content = content.replace('                        async def audio_interceptor():', '            async def audio_interceptor():')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Indentation fixed.")
