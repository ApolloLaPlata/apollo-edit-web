import re

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip BOM se existir no meio do codigo (FEFF)
text = text.replace('\ufeff', '')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w', encoding='utf-8') as f:
    f.write(text)
