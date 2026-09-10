import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

if 'from fastapi.responses import PlainTextResponse' not in text:
    text = 'from fastapi.responses import PlainTextResponse\n' + text

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
