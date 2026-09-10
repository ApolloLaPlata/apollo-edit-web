import os

html_path = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\public\\modal_ai_studio.html'
with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

if text.startswith('\ufeff'):
    text = text[1:]

try:
    # Ignorar chars que não mapeiam no cp1252 (como emojis reais misturados, se houver)
    # Mas a corrupção foi causada pelo PowerShell que pegou UTF-8 e salvou como CP1252.
    # Actually, let's just encode to cp1252 ignoring errors, but wait, replacing will lose emojis!
    # Let's see if there are emojis that were NOT corrupted.
    fixed_text = text.encode('cp1252', errors='ignore').decode('utf-8')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    
    html_path_2 = 'E:\\MEUS PROGRAMAS\\APOLLO_EDIT_WEB\\modal_ai_studio.html'
    with open(html_path_2, 'w', encoding='utf-8') as f:
        f.write(fixed_text)
    print("Sucesso!")
except Exception as e:
    print("Falha:", e)
