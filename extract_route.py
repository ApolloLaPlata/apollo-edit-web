import re
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.finditer(r'@app\.api_route\("/api/studio/modal/.*?"[\s\S]*?(?=\n@app|\Z)', text)
for m in matches:
    print(m.group(0))
