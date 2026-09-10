import sys

with open('/home/ubuntu/apollo_edit/servidor_web.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'if path == "generate/audio_lab":' in line:
        print(''.join(lines[i:i+50]))
        break
