import os
import glob

folder = 'E:/MEUS PROGRAMAS/APOLLO_EDIT_WEB/LABORATORIO_MODAIS'
files = glob.glob(f'{folder}/*.py')
count = 0

for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(f, 'r', encoding='latin-1') as file:
            content = file.read()
            
    if 'apollo-api-f5-tts' in content:
        new_content = content.replace('apollo-api-f5-tts', 'apollo-render-router')
        try:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
        except Exception:
            pass
        count += 1

print(f'Atualizado: {count} arquivos.')
