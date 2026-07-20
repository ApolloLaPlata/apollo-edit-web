import os
file = r"E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\basic_editor.py"
with open(file, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("raise Exception(\"Validation Error\")}\\n\\nDetalhes:\\n{e.stderr[-500:]}\")", "raise Exception(f\"Validation Error\\n\\nDetalhes:\\n{e.stderr[-500:]}\")")

with open(file, "w", encoding="utf-8") as f:
    f.write(content)
