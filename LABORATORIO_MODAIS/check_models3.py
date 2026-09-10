import re
with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    for line in f:
        if 'meta-llama' in line or 'nemotron' in line:
            print(line.strip())
