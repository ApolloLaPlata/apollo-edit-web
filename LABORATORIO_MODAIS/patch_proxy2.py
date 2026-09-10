import re

file_path = "E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/servidor_web.py"
with open(file_path, "r", encoding="utf-16-le") as f:
    content = f.read()

pattern = re.compile(r"yield json\.dumps\(\{\"status\": \"processing\", \"message\": \"Processando áudio na nuvem\.\.\.\"\}\)\.encode\('utf-8'\) \+ b'\\n'")
replacement = r"yield json.dumps({'status': 'processing', 'message': 'Processando áudio na nuvem...'}).encode('utf-8') + b' ' * 4096 + b'\n'"
content = pattern.sub(replacement, content)

pattern2 = re.compile(r"yield json\.dumps\(\{\"status\": \"processing\", \"message\": \"Iniciando geração de áudio no Modal\.\.\.\"\}\)\.encode\('utf-8'\) \+ b'\\n'")
replacement2 = r"yield json.dumps({'status': 'processing', 'message': 'Iniciando geração de áudio no Modal...'}).encode('utf-8') + b' ' * 4096 + b'\n'"
content = pattern2.sub(replacement2, content)

with open("E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS/servidor_web_fixed.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Proxy patched!")
