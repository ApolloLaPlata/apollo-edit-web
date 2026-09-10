import re

file_path = "/home/ubuntu/apollo_edit/servidor_web.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the broken line directly!
broken_line = r"yield json.dumps({\"status\": \"processing\", \"message\": \"Conectando ao roteador de ?udio na nuvem...\"}).encode('utf-8') + b'\n'"
fixed_line = "yield json.dumps({\"status\": \"processing\", \"message\": \"Conectando ao roteador de ?udio na nuvem...\"}).encode('utf-8') + b'\\n'"

content = re.sub(r"yield json\.dumps\(.*?Conectando ao roteador de ?udio na nuvem\.\.\..*?\)\.encode\('utf-8'\) \+ b'\n'", fixed_line, content, flags=re.DOTALL)
content = content.replace("yield json.dumps(data).encode('utf-8') + b'\n'", "yield json.dumps(data).encode('utf-8') + b'\\n'")
content = content.replace("yield line.encode('utf-8') + b'\n'", "yield line.encode('utf-8') + b'\\n'")
content = content.replace("yield json.dumps({\"status\": \"error\", \"message\": f\"Erro de Conex?o Nuvem-VPS: {str(e)}\"}).encode('utf-8') + b'\n'", "yield json.dumps({\"status\": \"error\", \"message\": f\"Erro de Conex?o Nuvem-VPS: {str(e)}\"}).encode('utf-8') + b'\\n'")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Strings multilinha convertidas de volta para barras invertidas literais!")
