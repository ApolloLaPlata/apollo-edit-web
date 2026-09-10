import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\api\routes_subtitles.py'
with open(file_path, 'rb') as f:
    raw_content = f.read()

# Tenta decodificar ignorando erros e salvar como utf-8 limpo
text_content = raw_content.decode('utf-8', errors='replace')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text_content)
print("Fix encoding de routes_subtitles.py")
