import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\cloud_tools\apollo_modal_engine.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('if isinstance(res, dict) and "audio" in res:', 'if isinstance(res, dict) and "audio_base64" in res:')
content = content.replace('res["audio"]', 'res["audio_base64"]')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Corrigido retorno do ACE-Step!")
