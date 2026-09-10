import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\servidor_web.py', 'r', encoding='utf-8') as f:
    for line in f:
        if '"model"' in line or "'model'" in line:
            print(line.strip())
