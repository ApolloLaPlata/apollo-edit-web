import os
import re

filepath = r'E:\MEUS PROGRAMAS\APOLLO_STUDIO\servidor_web.py'
with open(filepath, 'r', encoding='latin-1') as f:
    content = f.read()

def replacer_thumbnails(m):
    return 'user_prompt = f"Sugira 3 thumbnails para:\\n\\n{req.input_text}"'

def replacer_deepdive(m):
    return 'user_prompt = f"Aprofunde esta not\xedcia:\\n\\n{req.input_text}"'

content = re.sub(r'user_prompt = f"Sugira 3 thumbnails para:\s+\{req\.input_text\}"', replacer_thumbnails, content)
content = re.sub(r'user_prompt = f"Aprofunde esta not[^"]+:\s+\{req\.input_text\}"', replacer_deepdive, content)

with open(filepath, 'w', encoding='latin-1') as f:
    f.write(content)

print("servidor_web.py patched!")
