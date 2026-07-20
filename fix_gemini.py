import os
file = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\gemini_tts_api.py'
with open(file, 'r', encoding='utf-8') as f:
    content = f.read()

# Since the previous run failed due to a syntax error in the string, let's just use re to replace ANY print with Nenhuma API Key do Gemini configurada.
import re
content = re.sub(r'print\(.*?Nenhuma API Key do Gemini configurada.*?\)', 'print("[AVISO] Nenhuma API Key do Gemini configurada.")', content)

with open(file, 'w', encoding='utf-8') as f:
    f.write(content)
