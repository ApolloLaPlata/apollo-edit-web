import re
import os

hub_path = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\hub.html"
with open(hub_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if '<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 20px;">Acesso rápido a todos' in line:
        skip = True
        continue
    if skip and '</main>' in line:
        skip = False
        new_lines.append('        </main>\n')
        continue
    
    if not skip:
        new_lines.append(line)

with open(hub_path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed messy grid.")
