import sys

with open('/home/ubuntu/apollo_edit/backend/cloud_tools/apollo_modal_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

printing = False
for line in lines:
    if 'def api_generate_audio_lab' in line:
        printing = True
    if printing:
        print(line, end='')
    if printing and 'elif model == "minimax":' in line:
        break
