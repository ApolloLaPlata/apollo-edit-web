import sys
with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r') as f:
    text = f.read()

text = text.replace('if endpoint_name == "generate_image":', 'if path == "generate_image":')

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'w') as f:
    f.write(text)
