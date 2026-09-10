import os

file_path = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\modal_ai_studio.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("['img','vid','audio'].forEach(t => {", "['img','vid','audio','music'].forEach(t => {")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Corrigido o loop forEach das abas!")
