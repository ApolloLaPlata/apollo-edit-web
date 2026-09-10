import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '                                        "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",'
replacement = '                                        "model": "nvidia-nemotron-3-ultra-550b-a55b",'

content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("routes_studio.py modelo corrigido.")
