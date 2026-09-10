import sys

file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "yield json.dumps({\"status\": \"processing\", \"message\": \"Conectando ao roteador de ?udio na nuvem...\"}).encode('utf-8') + b'" in line:
        if line.endswith("b'\n"):
            lines[i] = line.replace("b'\n", "b'\\n'\n")
    if "yield json.dumps(data).encode('utf-8') + b'" in line:
        if line.endswith("b'\n"):
            lines[i] = line.replace("b'\n", "b'\\n'\n")
    if "yield line.encode('utf-8') + b'" in line:
        if line.endswith("b'\n"):
            lines[i] = line.replace("b'\n", "b'\\n'\n")
    if "yield json.dumps({\"status\": \"error\", \"message\": f\"Erro de Conex?o Nuvem-VPS: {str(e)}\"}).encode('utf-8') + b'" in line:
        if line.endswith("b'\n"):
            lines[i] = line.replace("b'\n", "b'\\n'\n")

# Extra fix if the line was split into TWO lines
for i in range(len(lines)):
    if "encode('utf-8') + b'" in lines[i] and lines[i].rstrip().endswith("b'"):
        # Combine this line and the next line, or just fix it directly
        lines[i] = lines[i].rstrip() + "\\n'\n"
        if lines[i+1].startswith("'"): # if there was a dangling quote on next line, remove it
            lines[i+1] = lines[i+1].replace("'", "", 1)

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Manual line fix applied!")
