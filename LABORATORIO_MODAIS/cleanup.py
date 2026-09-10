import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Remove debug routes
code = re.sub(r'@app\.get\("/debug_routes"\).*?return \{"routes": \[.*?\]\}\n', "", code, flags=re.DOTALL)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(code)
