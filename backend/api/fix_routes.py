import re

path = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/backend/api/routes_studio.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = 'keys = c.get("api_config", {}).get("api_keys", [])'
replacement = 'keys = c.get("api_config", {}).get("lightning_chat", {}).get("api_keys", [])'

content = content.replace(target, replacement)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("routes_studio.py corrigido.")
