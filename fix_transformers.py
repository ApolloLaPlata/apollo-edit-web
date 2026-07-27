import os

target_file = r'backend\cloud_tools\engines\universal_engine.py'
with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"transformers",', '"transformers<4.45.0",')

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
