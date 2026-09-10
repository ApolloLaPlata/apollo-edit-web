import re

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Procura o erro b" no final da linha e troca por b"\n"
text = text.replace('b"\n', 'b"\\n"')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
