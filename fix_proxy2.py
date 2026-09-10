import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

text = text.replace('"/api/studio/modal/{path}"', '"/api/studio/modal/{path:path}"')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
