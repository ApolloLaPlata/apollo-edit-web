import re

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

changes = {
    'Instruo': 'Instrução',
    'Interpretao': 'Interpretação',
    'irnico': 'irônico',
    'Catlogo': 'Catálogo',
    'Padro': 'Padrão',
    'Configuraes': 'Configurações',
    'avançado': 'Avançado',
    '?? ': '🎭 ',
    ' ': '📝 '
}

for k, v in changes.items():
    content = content.replace(k, v)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\public\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\web_ui\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

with open(r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\frontend\modal_ai_studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Mojibake fixed.")
