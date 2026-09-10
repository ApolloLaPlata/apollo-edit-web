import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'async def api_studio_modal_generate' in line:
        out = ''.join(lines[i:i+40])
        print(out.encode('ascii', 'ignore').decode('ascii'))
        break
