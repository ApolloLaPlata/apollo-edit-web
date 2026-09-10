import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

text = text.replace('endpoint_path = path.replace(\'_\', \'/\')', 'endpoint_path = path')
text = text.replace('{path:path}', '{path}')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
